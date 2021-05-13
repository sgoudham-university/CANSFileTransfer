import os
import sys

sys.path.append('..')
from common.status_code import StatusCode
from common.command import Command
from common.logger import Logger
from common.util import create_connection, send_file, send_message, recv_status_ack, is_file_present, \
    send_status_ack, recv_message, recv_listing, read_file


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
            STATUS_CODE = 4002
            STATUS_MESSAGE = ""

            # Send Server request information
            self.LOGGER.info(f"Sending Request '{self.request}' To Specified Server! [...]")
            status, status_message = send_message(self, self.socket, self.request, HEADER_SIZE)
            if not status: break

            # Receive acknowledgement for request type. If not successful, terminate connection
            request_status = recv_status_ack(self, self.socket, 4000, SEPARATOR, HEADER_SIZE)
            if not request_status: break

            if self.request == Command.PUT:
                file_path = os.path.join("data", self.file)

                # Check if file doesn't exist within client. If file doesn't exist, terminate connection
                if not is_file_present(file_path):
                    self.LOGGER.status_code(StatusCode.code[3006])
                    STATUS_CODE = 3006
                    send_status_ack(self, self.socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                    break

                # Send status acknowledgement that file exists locally
                STATUS_CODE = 4005
                send_status_ack(self, self.socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                # Receive status acknowledgement that Server is ready to receive file information
                server_status = recv_status_ack(self, self.socket, 4008, SEPARATOR, HEADER_SIZE)
                if not server_status: break

                file_size = os.path.getsize(os.path.join("data", self.file))

                # Send file information (file_size and file_name) to Server
                self.LOGGER.info(f"Sending File Information For '{self.file}' To Specified Server! [...]")
                message = f"{self.file}{SEPARATOR}{file_size}"
                status, status_message = send_message(self, self.socket, message, HEADER_SIZE)
                if not status: break

                # Receive status acknowledgement that request is valid, terminate connection if not successful
                transfer_file_status = recv_status_ack(self, self.socket, 4003, SEPARATOR, HEADER_SIZE)
                if not transfer_file_status: break

                # Transfer file through buffering
                file_data_status, file_data_status_msg = send_file(self, self.socket, file_path, file_size)
                if not file_data_status: break

                # Receive acknowledgement from server about put request success
                put_request_status = recv_status_ack(self, self.socket, 4002, SEPARATOR, HEADER_SIZE)
                if not put_request_status: break

            elif self.request == Command.GET:
                file_path = os.path.join("data", self.file)
                # Check if file already exists within client. If file does exist, terminate connection
                if is_file_present(file_path):
                    self.LOGGER.status_code(StatusCode.code[3007])
                    STATUS_CODE = 3007
                    send_status_ack(self, self.socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                    break

                # Send acknowledgement that Client is ready to receive file
                STATUS_CODE = 4004
                send_status_ack(self, self.socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                # Receive status acknowledgement that Server is ready to receive file information
                server_status = recv_status_ack(self, self.socket, 4008, SEPARATOR, HEADER_SIZE)
                if not server_status: break

                # Send file information (file_name) to Server
                self.LOGGER.info(f"Sending File Information For '{self.file}' To Specified Server! [...]")
                status, status_message = send_message(self, self.socket, self.file, HEADER_SIZE)
                if not status: break

                # Receive status acknowledgement that file is now valid
                file_status = recv_status_ack(self, self.socket, 4009, SEPARATOR, HEADER_SIZE)
                if not file_status: break

                # Send acknowledgement that Client is ready to receive file_size
                STATUS_CODE = 4010
                send_status_ack(self, self.socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                # Retrieve file_size
                file_size = recv_message(self, self.socket, SEPARATOR, HEADER_SIZE)
                if not file_size: break

                # Send acknowledgement that Client is ready for file transfer (receiving file_data)
                STATUS_CODE = 4003
                send_status_ack(self, self.socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                # Receive file_data and write into local file
                status, status_message = read_file(self, self.socket, self.file, file_size)

                # Send status acknowledgement if get request was successful or not
                if not status:
                    STATUS_CODE = 3001
                    STATUS_MESSAGE = status_message
                else:
                    STATUS_CODE = 4002
                    STATUS_MESSAGE = f"[{self.request}, {self.file}]"
                self.LOGGER.status_code(StatusCode.code[STATUS_CODE] + STATUS_MESSAGE)
                send_status_ack(self, self.socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

            elif self.request == Command.LIST:
                # Send acknowledgement to Server that Client is ready to receive Server directory size
                STATUS_CODE = 4007
                send_status_ack(self, self.socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                # Retrieve Server directory information (size of server_dir)
                self.LOGGER.info(f"Retrieving Server Directory Information! [...]")
                server_dir_size = recv_message(self, self.socket, SEPARATOR, HEADER_SIZE)
                if not server_dir_size: break

                # Send acknowledgement that Server directory size was received successfully
                STATUS_CODE = 4006
                send_status_ack(self, self.socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

                # Receive server listing
                dir_listing_dict, status_message = recv_listing(self, self.socket, int(server_dir_size))
                if not dir_listing_dict:
                    STATUS_CODE = 3002
                    STATUS_MESSAGE = status_message
                    send_status_ack(self, self.socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
                    break

                # Display Server directory
                self.LOGGER.info("Current Server Directory:")
                self.LOGGER.print_dir(dir_listing_dict)

                # Send acknowledgement that list request was successful
                STATUS_CODE = 4002
                STATUS_MESSAGE = f"[{self.request}]"
                self.LOGGER.status_code(StatusCode.code[STATUS_CODE] + STATUS_MESSAGE)
                send_status_ack(self, self.socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)

            connection = False
        self.socket.close()


def main():
    client = Client()
    client.handle()


if __name__ == "__main__":
    main()
