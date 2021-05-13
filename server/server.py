import json
import os
import socket
import sys

sys.path.append('..')
from common.status_code import StatusCode
from common.command import Command
from common.logger import Logger
from common.util import create_connection, read_file, is_file_present, send_status_ack, recv_message, recv_status_ack, \
    get_dir, send_message, send_listing, send_file


class Server:
    """
    Class Representing a Server

    --> This server will constantly listen for any incoming client connections on the given port.

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
                    request_type = recv_message(self, cli_socket, SEPARATOR, HEADER_SIZE)
                    if not request_type: break
                    self.request = request_type

                    # Send status acknowledgement that request_type was received successfully
                    STATUS_CODE = 4000
                    send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                    if request_type == Command.PUT:
                        # If client does not have file locally, terminate connection
                        list_request_status = recv_status_ack(self, cli_socket, 4005, SEPARATOR, HEADER_SIZE)
                        if not list_request_status: break

                        # Send status acknowledgement that Server is ready to receive file information
                        STATUS_CODE = 4008
                        send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                        # Receive file_name & file_size.
                        file_information = recv_message(self, cli_socket, SEPARATOR, HEADER_SIZE)
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

                        # Check if file already exists. If file already exists, terminate connection
                        file_path = os.path.join("data", file_name)
                        if is_file_present(file_path):
                            self.LOGGER.status_code(StatusCode.code[3005])
                            STATUS_CODE = 3005
                            send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                            break

                        # Send status acknowledgement that the put request is now valid
                        STATUS_CODE = 4003
                        send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                        # Receive file_data and write into local file
                        status, status_message = read_file(self, cli_socket, file_name, file_size)

                        # Send status acknowledgement if put request was successful or not
                        if not status:
                            STATUS_CODE = 3001
                            STATUS_MESSAGE = status_message
                        else:
                            STATUS_CODE = 4002
                            STATUS_MESSAGE = f"[{request_type}, {file_name}]"
                        self.LOGGER.status_code(StatusCode.code[STATUS_CODE] + STATUS_MESSAGE)
                        send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                    elif request_type == Command.GET:
                        # If client has file locally, terminate connection
                        get_request_status = recv_status_ack(self, cli_socket, 4004, SEPARATOR, HEADER_SIZE)
                        if not get_request_status: break

                        # Send status acknowledgement that Server is ready to receive file information
                        STATUS_CODE = 4008
                        send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                        # Receive file_name
                        file_name = recv_message(self, cli_socket, SEPARATOR, HEADER_SIZE)
                        if not request_type: break

                        file_path = os.path.join("data", file_name)
                        # Check if file doesn't exist locally. If file doesn't exist, terminate connection
                        if not is_file_present(file_path):
                            self.LOGGER.status_code(StatusCode.code[3004])
                            STATUS_CODE = 3004
                            send_status_ack(self, self.socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                            break

                        # Send status acknowledgement that file is valid
                        STATUS_CODE = 4009
                        send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                        # If client not ready to receive file_size, terminate connection
                        client_status = recv_status_ack(self, cli_socket, 4004, SEPARATOR, HEADER_SIZE)
                        if not client_status: break

                        file_size = os.path.getsize(os.path.join("data", file_name))
                        # Send file information (file_size) to Client
                        self.LOGGER.info(f"Sending File Information For '{self.file}' To Specified Client! [...]")
                        status, status_message = send_message(self, cli_socket, file_size, HEADER_SIZE)
                        if not status: break

                        # If client not ready for file transfer, terminate connection
                        client_status = recv_status_ack(self, cli_socket, 4003, SEPARATOR, HEADER_SIZE)
                        if not client_status: break

                        # Transfer file through buffering
                        file_data_status, file_data_status_msg = send_file(self, cli_socket, file_path, file_size)
                        if not file_data_status: break

                        # Receive acknowledgement about get request success
                        get_request_status = recv_status_ack(self, self.socket, 4002, SEPARATOR, HEADER_SIZE)
                        if not get_request_status: break

                    elif request_type == Command.LIST:
                        # If Client is not ready to receive Server directory size, terminate connection
                        client_status = recv_status_ack(self, cli_socket, 4007, SEPARATOR, HEADER_SIZE)
                        if not client_status: break

                        server_listing_dict = get_dir(os.path.join("data"))

                        # Send directory information to Client (amount of bytes to receive)
                        self.LOGGER.info(f"Sending Directory Information To Client! [...]")
                        message = str(len(json.dumps(server_listing_dict).encode('utf-8')))
                        status, status_message = send_message(self, cli_socket, message, HEADER_SIZE)
                        if not status: break

                        # If Client did not get Server Directory information, terminate connection
                        server_listing_size_status = recv_status_ack(self, cli_socket, 4006, SEPARATOR, HEADER_SIZE)
                        if not server_listing_size_status: break

                        # Send Server listing to Client
                        status, status_message = send_listing(self, cli_socket, server_listing_dict)
                        if not status: break

                        # Receive acknowledgement from Client if list request was successful or not
                        list_request_status = recv_status_ack(self, cli_socket, 4002, SEPARATOR, HEADER_SIZE)
                        if not list_request_status: break

                    connection = False
                cli_socket.close()


def main():
    server = Server()
    server.handle()


if __name__ == "__main__":
    main()
