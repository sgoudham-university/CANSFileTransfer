import os
import socket
import sys

sys.path.append('..')
from common.status_code import StatusCode
from common.command import Command
from common.logger import Logger
from common.util import create_connection, read_file, recv_message


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

        :returns:
        """

        try:
            self.PORT = sys.argv[1]
        except IndexError:
            print(StatusCode.code[2002])
            sys.exit(1)

    def handle(self):
        """"""

        HEADER_SIZE = 32
        SEPARATOR = ' ' * HEADER_SIZE
        STATUS_CODE = None
        STATUS_MESSAGE = ""

        while True:
            try:
                cli_socket, cli_address = self.SOCKET.accept()
            except socket.error:
                self.LOGGER.status_code(StatusCode.code[2000])
                sys.exit(1)
            except Exception as exp:
                self.LOGGER.unknown_error(exp)
                sys.exit(1)
            else:
                connection = True
                while connection:
                    header, overflow = recv_message(cli_socket, HEADER_SIZE, self.LOGGER)
                    if not header: break

                    request_type, file_name = header.split(SEPARATOR)

                    if request_type == Command.PUT:
                        status = read_file(self, cli_socket, file_name, overflow, HEADER_SIZE)
                        if not status:
                            STATUS_CODE = 3000
                            STATUS_MESSAGE = status
                        else:
                            STATUS_CODE = 4000

                    elif request_type == Command.GET:
                        pass
                        # call send_file
                    elif request_type == Command.LIST:
                        pass

                    # message = f"{STATUS_CODE}{SEPARATOR}{STATUS_MESSAGE}"
                    # header = f"{len(message):<{HEADER_SIZE}}" + message
                    # cli_socket.sendall(header.encode('utf-8'))

                    connection = False
                    self.LOGGER.status_code(StatusCode.code[2001])
                cli_socket.close()


def main():
    server = Server()
    server.handle()


if __name__ == "__main__":
    main()
