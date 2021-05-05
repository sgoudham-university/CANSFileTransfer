import os
import socket
import sys

sys.path.append('..')
from common.status_code import StatusCode
from common.command import Command
from common.logger import Logger
from common.util import create_connection, read_file, isFilePresent, send_status_ack, recv_request


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
            STATUS_CODE = 4000
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
                    request_type, file_name, file_size = recv_request(self, cli_socket, SEPARATOR, HEADER_SIZE)
                    if not request_type: break

                    if request_type == Command.PUT:
                        # Check if file already exists, terminate connection if file exists on server
                        file_path = os.path.join("data", file_name)
                        if isFilePresent(file_path):
                            self.LOGGER.status_code(StatusCode.code[3005])
                            STATUS_CODE = 3005
                            send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                            break
                        else:
                            send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                        # Receive file_data and write into file
                        status, status_message = read_file(self, cli_socket, file_name, file_size)

                        # Send acknowledgement back to client if file transfer was successful or not
                        if not status:
                            STATUS_CODE = 3001
                            STATUS_MESSAGE = status_message
                        else:
                            STATUS_CODE = 4001
                        send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                    elif request_type == Command.GET:
                        # Check if file already exists, terminate connection if file does not exist on server
                        file_path = os.path.join("data", file_name)
                        if not isFilePresent(file_path):
                            self.LOGGER.status_code(StatusCode.code[3004])
                            STATUS_CODE = 3004
                            send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                            break
                        else:
                            send_status_ack(self, cli_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                    elif request_type == Command.LIST:
                        pass

                    connection = False
                cli_socket.close()


def main():
    server = Server()
    server.handle()


if __name__ == "__main__":
    main()
