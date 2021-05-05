import sys

sys.path.append('..')
from common.status_code import StatusCode
from common.command import Command
from common.logger import Logger
from common.util import create_connection, transfer_file, send_request, recv_status_ack


class Client:
    """
    Class Representing a Client

    --> This client will take in 4 arguments: host, port, request and file (file being optional)
    --> A timeout of 100 seconds has been implemented to ensure that the client does not endlessly listen and waste
        system resources.

    --> Included functionality includes:
        -> PUT: Receive requested filename from user and put requested file onto targeted server
        -> GET: Receive requested file from user get requested file from the targeted server
        -> LIST: Return the targeted server's data directory
    """

    def __init__(self):
        self.host = None
        self.port = None
        self.request = None
        self.file = None
        self.socket = None
        self.LOGGER = None

        self.get_arguments()

        self.LOGGER = Logger(self.host, self.port)
        self.socket = create_connection(self.host, self.port, "client", self.LOGGER)

    def get_arguments(self):
        """
        Get information from user for connection setup, type of command and potentially a file

        :returns: None
        """

        try:
            self.host = sys.argv[1]
            self.port = sys.argv[2]
            self.request = sys.argv[3]

            if self.request == Command.PUT or self.request == Command.GET:
                self.file = sys.argv[4]
        except IndexError:
            print(StatusCode.code[1000])
            sys.exit(1)

    def handle(self):
        """
        Main 'handle' Method for Client

        :returns: None
        """

        HEADER_SIZE = 32
        SEPARATOR = ' ' * HEADER_SIZE
        connection = True

        while connection:
            if self.request == Command.PUT:
                self.LOGGER.info(f"Sending Request For '{self.file}'! [...]")
                status, status_message = send_request(self, HEADER_SIZE, SEPARATOR)
                if not status: break

                request_status, message_overflow = recv_status_ack(self, 4000, SEPARATOR, HEADER_SIZE)
                if not request_status: break

                self.LOGGER.info(f"Transmitting '{self.file}' [...]")
                file_data_status = transfer_file(self)
                if not file_data_status:
                    self.LOGGER.status_code(StatusCode.code[3001] + file_data_status)
                    break

                put_request_status, new_overflow = recv_status_ack(self, 4001, SEPARATOR, HEADER_SIZE, message_overflow)
                if not put_request_status: break

            elif self.request == Command.GET:
                pass
                # call recv_file
            elif self.request == Command.LIST:
                pass
                # call recv_listing
            else:
                self.LOGGER.status_code(StatusCode.code[1001])
                sys.exit(1)

            connection = False
        self.socket.close()


def main():
    client = Client()
    client.handle()


if __name__ == "__main__":
    main()
