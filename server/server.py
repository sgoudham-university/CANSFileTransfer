import os
import socket
import sys

sys.path.append('..')
from common.command import Command
from common.logger import Logger
from common.util import create_connection, recv_header, recv_message


class Server:
    def __init__(self):
        self.HOST = ""
        self.PORT = None
        self.COMMAND = None
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

        while True:
            try:
                cli_socket, cli_address = self.SOCKET.accept()
            except socket.error:
                self.LOGGER.info("Timed Out - No Client Connection Received - Closing Server [...]")
                sys.exit(1)
            except Exception as exp:
                self.LOGGER.error(exp)
                sys.exit(1)
            else:
                connection = True
                while connection:
                    header, overflow = recv_header(cli_socket, HEADER_SIZE, self.LOGGER)
                    if not header: break

                    REQUEST_TYPE, FILE_NAME = header.split(SEPARATOR)

                    with open(os.path.join(self.DATA, FILE_NAME), "wb") as file:
                        while True:
                            file_data, new_overflow = recv_message(cli_socket, HEADER_SIZE, overflow, self.LOGGER)
                            if not file_data: break
                            file.write(file_data)
                            overflow = new_overflow

                    # file_name_bytes_recv = 0
                    # message = ""
                    # while file_name_bytes_recv < FILE_NAME_BYTES_SIZE:
                    #     request = cli_socket.recv(32)
                    #     if not request: break
                    #     file_name_bytes_recv += len(request)
                    #     message += request.decode('utf-8')

                    if self.COMMAND == Command.PUT:
                        pass
                        # call recv_file
                    elif self.COMMAND == Command.GET:
                        pass
                        # call send_file
                    elif self.COMMAND == Command.LIST:
                        pass

                    connection = False
                cli_socket.close()

            # call send_listing

            # while True:
            #     received = True
            #     cli_sock, cli_addr = self.SOCKET.accept()
            #
            #     while received:
            #         request = cli_sock.recv(1024)
            #
            #         if request.decode('utf-8') == "EXIT":
            #             received = False
            #         else:
            #             print(request.decode('utf-8'))
            #
            #             input_message = input("Please enter the message that you want to send: ")
            #
            #             if input_message == "EXIT":
            #                 received = False
            #             cli_sock.sendall(input_message.encode('utf-8'))
            #
            #     cli_sock.close()


def main():
    server = Server()
    server.handle()


if __name__ == "__main__":
    main()
