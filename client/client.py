import os
import sys

sys.path.append('..')
from common.command import Command
from common.logger import Logger
from common.util import isValidFile, create_connection


class Client:
    def __init__(self):
        self.HOST = None
        self.PORT = None
        self.COMMAND = None
        self.FILE = None
        self.SOCKET = None
        self.LOGGER = None

        self.get_arguments()

        self.LOGGER = Logger(self.HOST, self.PORT)
        self.SOCKET = create_connection(self.HOST, self.PORT, "client", self.LOGGER)

    def get_arguments(self):
        """
        Get information from user for connection setup, type of command and potentially a file
        """

        try:
            self.HOST = sys.argv[1]
            self.PORT = sys.argv[2]
            self.COMMAND = sys.argv[3]
            self.FILE = sys.argv[4]
        except IndexError as ixe:
            print(
                "Arguments are Missing! E.g [python client.py <HOST> <PORT> <REQUEST> | python client.py <HOST> <PORT> <REQUEST> <FILE>]")
            sys.exit(1)

    def handle(self):
        """"""
        HEADER_SIZE = 32
        SEPARATOR = ' ' * HEADER_SIZE

        connection = True
        while connection:

            if self.COMMAND == Command.PUT:
                file_path = os.path.join("data", self.FILE)
                if not isValidFile(file_path):
                    self.LOGGER.info(f"File '{self.FILE}' Not Found! Closing Client [...]")
                    sys.exit(1)

                message = f"{self.COMMAND}{SEPARATOR}{self.FILE}"
                header = f"{len(message):<{HEADER_SIZE}}" + message

                self.SOCKET.send(header.encode('utf-8'))

                with open(file_path, 'rb', 256) as file:
                    while True:
                        message = file.read(1024)
                        if not message: break
                        header = f"{len(message):<{HEADER_SIZE}}" + message.decode('utf-8')
                        self.SOCKET.sendall(header.encode('utf-8'))

                # Send the request type, filename and file_data as one

                # Generate Header Message with type of request, size of filename and file data in bytes
                # Send over header message

                # send over filename

                # stream file through in small chunks at a time

                # cli_socket.sendall(input_message.encode('utf-8'))
            elif self.COMMAND == Command.GET:
                pass
                # call recv_file
            elif self.COMMAND == Command.LIST:
                pass
                # call recv_listing
            else:
                self.LOGGER.info(f"Command '{self.COMMAND}' Not Recognised! Closing Client [...]")
                sys.exit(1)

            connection = False
        self.SOCKET.close()

        # received = True
        # while received:
        #     input_message = input("Please enter the message that you want to send: ")
        #
        #     if input_message == "EXIT":
        #         received = False
        #         self.SOCKET.sendall(input_message.encode('utf-8'))
        #     else:
        #         self.SOCKET.sendall(input_message.encode('utf-8'))
        #         request = self.SOCKET.recv(1024)
        #
        #         if request.decode('utf-8') == "EXIT":
        #             received = False
        #         else:
        #             print(request.decode('utf-8'))
        #
        # self.SOCKET.close()


def main():
    client = Client()
    client.handle()


if __name__ == "__main__":
    main()
