import sys

sys.path.append('..')
from common.status_code import StatusCode
from common.command import Command
from common.logger import Logger
from common.util import create_connection, transfer_file


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
        except IndexError:
            print(StatusCode.code[1000])
            sys.exit(1)

    def handle(self):
        """"""

        HEADER_SIZE = 32
        SEPARATOR = ' ' * HEADER_SIZE
        connection = True

        while connection:
            if self.COMMAND == Command.PUT:
                self.LOGGER.info(f"Sending File '{self.FILE}'! [...]")
                status = transfer_file(self, SEPARATOR, HEADER_SIZE)
                if not status:
                    self.LOGGER.status_code(StatusCode.code[3000] + status)
                    break

            elif self.COMMAND == Command.GET:
                pass
                # call recv_file
            elif self.COMMAND == Command.LIST:
                pass
                # call recv_listing
            else:
                self.LOGGER.status_code(StatusCode.code[1001])
                sys.exit(1)

            # status_header, new_overflow = recv_message(self.SOCKET, HEADER_SIZE, self.LOGGER)
            # print(status_header)
            # if not status_header: break

            connection = False
        self.SOCKET.close()


def main():
    client = Client()
    client.handle()


if __name__ == "__main__":
    main()
