import os
import socket
import sys

sys.path.append('..')
from common.status_code import StatusCode
from common.command import Command
from common.logger import Logger
from common.util import create_connection, read_file, isFilePresent, send_status_ack, recv_request, recv_status_ack


class Server:
    """
    Class Representing a Server

    --> This server will constantly listen for any incoming client connections on the given port.
    --> A timeout of 100 seconds has been implemented to ensure that the server does not endlessly listen and waste
        system resources.

    --> Included functionality includes:
        -> PUT: Receive file from client and write to local directory
        -> GET: Receive requested file from client and send file data to client
        -> LIST: Return the current server data directory
    """

    def __init__(self):
        self.host = ""
        self.port = None
        self.request = None
        self.file = None
        self.socket = None
        self.LOGGER = None
        self.data = os.path.join("data")

        self.get_arguments()

        self.LOGGER = Logger(self.host, self.port)
        self.socket = create_connection(self.host, self.port, "server", self.LOGGER)

    def get_arguments(self):
        """
        Get port to listen for client connections

        :returns: None
        """

        try:
            self.port = sys.argv[1]
        except IndexError:
            print(StatusCode.code[2002])
            sys.exit(1)

    def handle(self):
        """
        Main 'handle' Method for Server

        --> A default success status code of 4000 has been assumed given a new client connection.

        :returns: None
        """

        HEADER_SIZE = 32
        SEPARATOR = ' ' * HEADER_SIZE

        while True:
            STATUS_CODE = 4002
            STATUS_MESSAGE = ""

            self.LOGGER.host = self.host
            self.LOGGER.port = self.port
            self.LOGGER.status_code(StatusCode.code[2001])

            try:
                cli_socket, cli_address = self.socket.accept()
            except socket.error:
                self.LOGGER.status_code(StatusCode.code[2000])
                sys.exit(1)
            except Exception as exp:
                self.LOGGER.unknown_error(exp)
                sys.exit(1)
            else:
                self.LOGGER.host = cli_address[0]
                self.LOGGER.port = cli_address[1]
                connection = True

                while connection:
                    # Receive initial request type from client
                    request_type = recv_request(self, cli_socket, SEPARATOR, HEADER_SIZE)
                    if not request_type: break
                    self.request = request_type

                    # Send acknowledgement back to client that request_type was received successfully
                    STATUS_CODE = 4000
                    send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                    if request_type == Command.PUT:
                        # If client does not have file locally, terminate connection
                        client_file_status = recv_status_ack(self, cli_socket, 4005, SEPARATOR, HEADER_SIZE)
                        if not client_file_status: break

                        # Receive file_name & file_size.
                        file_information = recv_request(self, cli_socket, SEPARATOR, HEADER_SIZE)
                        if not request_type: break

                        # Split variables. If malformed file information, terminate connection
                        try:
                            file_name, file_size = file_information.split(SEPARATOR)
                            file_size = int(file_size)
                        except ValueError as vle:
                            self.LOGGER.status_code(StatusCode.code[3000] + vle)
                            STATUS_CODE = 3000
                            STATUS_MESSAGE = vle
                            send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                            break

                        # Send acknowledgement back to client that filename and filesize was received successfully
                        STATUS_CODE = 4001
                        send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                        # Check if file already exists. If file already exists, terminate connection
                        file_path = os.path.join("data", file_name)
                        if isFilePresent(file_path):
                            self.LOGGER.status_code(StatusCode.code[3005])
                            STATUS_CODE = 3005
                            send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                            break

                        # Send acknowledgement back to client that the full request is now valid
                        STATUS_CODE = 4003
                        send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                        # Receive file_data and write into local file
                        status, status_message = read_file(self, cli_socket, file_name, file_size)

                        # Send acknowledgement back to client if put request was successful or not
                        if not status:
                            STATUS_CODE = 3001
                            STATUS_MESSAGE = status_message
                        else:
                            STATUS_CODE = 4002
                        send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                    elif request_type == Command.GET:
                        pass
                        # # If client has file locally, terminate connection
                        # client_file_status = recv_status_ack(self, cli_socket, 4001, SEPARATOR, HEADER_SIZE)
                        # if not client_file_status: break
                        #
                        # file_information = recv_request(self, cli_socket, SEPARATOR, HEADER_SIZE)
                        # if not request_type: break
                        #
                        # # Receive file_name. Terminate connection if malformed request_header
                        # try:
                        #     file_name, file_size = file_information.split(SEPARATOR)
                        #     file_size = int(file_size)
                        # except ValueError as vle:
                        #     self.LOGGER.status_code(StatusCode.code[3000] + vle)
                        #     STATUS_CODE = 3000
                        #     STATUS_MESSAGE = vle
                        #     send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                        #     break
                        #
                        # # Send acknowledgement back to client that filename and filesize was received successfully
                        # STATUS_CODE = 4001
                        # send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                        #
                        # # Receive filename
                        #
                        # # Send acknowledgement that file information was successfully retrieved
                        #
                        # # Check if file already exists, terminate connection if file does not exist on server
                        # file_path = os.path.join("data", file_name)
                        # if not isFilePresent(file_path):
                        #     self.LOGGER.status_code(StatusCode.code[3004])
                        #     STATUS_CODE = 3004
                        #     send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                        #     break
                        # else:
                        #     send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                        #
                        # # Send over requested file size to the client
                        #
                        # # Send over requested file data to the client
                        # file_transfer_status, file_transfer_status_msg = transfer_file(self, cli_socket, file_path,
                        #                                                                file_size)
                        #
                        # # Send acknowledgement back to client if file transfer was successful or not
                        # if not file_transfer_status:
                        #     self.LOGGER.status_code(StatusCode.code[3001] + file_transfer_status_msg)
                        #     STATUS_CODE = 3001
                        #     STATUS_MESSAGE = file_transfer_status_msg
                        #     send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                        #     break
                        # else:
                        #     STATUS_CODE = 4002
                        #     send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                    elif request_type == Command.LIST:
                        pass

                    connection = False
                cli_socket.close()


def main():
    server = Server()
    server.handle()


if __name__ == "__main__":
    main()
