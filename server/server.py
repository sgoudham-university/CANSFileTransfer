import os
import socket
import sys

sys.path.append('..')
from common.status_code import Error
from common.command import Command
from common.logger import Logger
from common.util import create_connection, recv_header, write_file


class Server:
    def __init__(self):
        self.HOST = ""
        self.PORT = None
        self.FILE = None
        self.SOCKET = None
        self.LOGGER = None
        self.DATA = os.path.join("data")

        self.get_arguments()

        self.LOGGER = Logger(self.HOST, self.PORT)
        self.SOCKET = create_connection(self.HOST, self.PORT, "server", self.LOGGER)

    def get_arguments(self):
        """

        :return:
        """

        if len(sys.argv) >= 2:
            self.PORT = sys.argv[1]

    def handle(self):
        """"""

        HEADER_SIZE = 32
        SEPARATOR = ' ' * HEADER_SIZE
        STATUS_CODE = None

        while True:
            try:
                cli_socket, cli_address = self.SOCKET.accept()
            except socket.error:
                self.LOGGER.status_code(Error.FOUR)
                sys.exit(1)
            except Exception as exp:
                self.LOGGER.unknown_error(exp)
                sys.exit(1)
            else:
                connection = True

                while connection:

                    header = recv_header(cli_socket, HEADER_SIZE, self.LOGGER)
                    if not header: break

                    REQUEST_TYPE, FILE_NAME, FILE_DATA_BYTES = header.split(SEPARATOR)

                    if REQUEST_TYPE == Command.PUT:
                        write_file(self, FILE_NAME, FILE_DATA_BYTES)
                    elif REQUEST_TYPE == Command.GET:
                        pass
                        # call send_file
                    elif REQUEST_TYPE == Command.LIST:
                        pass

                    connection = False

                cli_socket.close()

            # call send_listing


def main():
    server = Server()
    server.handle()


if __name__ == "__main__":
    main()
