import os
import sys

sys.path.append('..')
from common.status_code import Error, Success
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
            print(Error.ONE)
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
                    self.LOGGER.status_code(Error.THREE)
                    sys.exit(1)

                self.LOGGER.info(f"Reading File '{self.FILE}'! [...]")
                target_file_bytes = open(file_path, 'rb').read()

                self.LOGGER.info(f"Sending File '{self.FILE}'! [...]")
                message = f"{self.COMMAND}{SEPARATOR}{self.FILE}{SEPARATOR}{target_file_bytes.decode('utf-8')}"
                header = f"{len(message):<{HEADER_SIZE}}" + message

                self.SOCKET.send(header.encode('utf-8'))

                self.LOGGER.status_code(Success.ONE)

            elif self.COMMAND == Command.GET:
                pass
                # call recv_file
            elif self.COMMAND == Command.LIST:
                pass
                # call recv_listing
            else:
                self.LOGGER.status_code(Error.TWO)
                sys.exit(1)

            connection = False
        self.SOCKET.close()

        # tracemalloc.start()
        # target_file_bytes = b''
        # with open(file_path, 'rb') as target_file:
        #     while True:
        #         file_chunk = target_file.read(10000024)
        #         print(file_chunk)
        #         if file_chunk == b'': break
        #         target_file_bytes += file_chunk
        # current, peak = tracemalloc.get_traced_memory()
        # print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
        # tracemalloc.stop()


def main():
    client = Client()
    client.handle()


if __name__ == "__main__":
    main()
