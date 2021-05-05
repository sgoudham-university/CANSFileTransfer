import os
import socket
import sys

from common.status_code import StatusCode


def create_connection(host, port, local_machine, LOGGER):
    """
    Instantiates a connection for the given machine (client/server)

    :param host: Host of target machine
    :param port: Port of target machine
    :param local_machine: The machine creating the connection
    :param LOGGER: Logger to log information to the given local_machine

    :returns: None
    """

    try:
        general_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        general_socket.settimeout(100)

        if local_machine == "client":
            general_socket.connect((host, int(port)))
        elif local_machine == "server":
            general_socket.bind((host, int(port)))
            general_socket.listen(5)
    except socket.error as soe:
        LOGGER.info(soe)
        sys.exit(1)
    except Exception as exp:
        LOGGER.unknown_error(exp)
        sys.exit(1)
    else:
        if local_machine == "client":
            LOGGER.info(f"Successfully Connected to [{host}:{port}]")
        elif local_machine == "server":
            LOGGER.info(f"Booting Server [...]")
            LOGGER.info(f"Server Online!")

        return general_socket


def recv_message(general_socket, HEADER_SIZE, LOGGER, previous_overflow=""):
    """
    Method for receiving messages from the client or the server.

    --> A "Fixed-Length Header" has been implemented with support for message overflow
        --> E.g Format of Message '5                             Hello'
        --> '5' is the length of the actual message to be retrieved
        --> 'Hello' is the content of the actual message (5 bytes)

    --> The 'overflow' on a message may occur when the target machine sends multiple messages at once but then is
        caught within a single recv(), this method ensures that any overflow is captured and returned at the end to be
        carried over to the next call of recv()


    :param general_socket: Client/Server socket
    :param HEADER_SIZE: Characters used to separate meaningful information from length of message
    :param LOGGER: Logger to log information to the calling machine (client/server)
    :param previous_overflow: Any previous overflow received from the previous recv() (if any)

    :returns: complete_message, current_overflow
    """

    complete_message = ""
    complete_message += previous_overflow
    current_overflow = previous_overflow
    message_length = 0
    incoming_message = True

    try:
        while True:
            request = general_socket.recv(204800)
            if not request: break
            complete_message += request.decode("utf-8")

            if incoming_message:
                message_length = int(complete_message[:HEADER_SIZE])
                incoming_message = False

            if len(complete_message) - HEADER_SIZE >= message_length:
                header_with_overflow = complete_message[HEADER_SIZE:]
                complete_message = header_with_overflow[:message_length]
                current_overflow = header_with_overflow[message_length:]
                break
    except socket.error as soe:
        LOGGER.info(soe)
        return False, soe
    except Exception as exp:
        LOGGER.unknown_error(exp)
        return False, exp
    else:
        LOGGER.info(f"Header Received! [{', '.join(complete_message.split())}]")
        return complete_message, current_overflow


def send_request(self, HEADER_SIZE, SEPARATOR):
    """
    Method for sending the initial request to the targeted server

    :param self: Client instance
    :param HEADER_SIZE: Characters used to separate meaningful information from length of message
    :param SEPARATOR: Characters to split the request by

    :returns: True, True (if successful)
    """

    try:
        file_size = os.path.getsize(os.path.join("data", self.file))
        message = f"{self.request}{SEPARATOR}{self.file}{SEPARATOR}{file_size}"
        header = f"{len(message):<{HEADER_SIZE}}" + message
        self.socket.sendall(header.encode('utf-8'))
    except socket.error as soe:
        self.LOGGER.info(soe)
        return False, soe
    except Exception as exp:
        self.LOGGER.unknown_error(exp)
        return False, exp
    else:
        return True, True


def recv_request(self, general_socket, SEPARATOR, HEADER_SIZE):
    """
    Receive the initial request from the client

    :param self: Server Instance
    :param general_socket: Client/Server socket
    :param SEPARATOR: Characters to split the request by
    :param HEADER_SIZE: Characters used to separate meaningful information from length of message

    :returns: request_type, file_name, file_size (if successful)
    """

    # Receive initial request, terminate connection if data malformed
    request, overflow = recv_message(general_socket, HEADER_SIZE, self.LOGGER)
    if not request:
        STATUS_CODE = 3000
        STATUS_MESSAGE = overflow   # variable 'overflow' may also contain an error message
        send_status_ack(self, general_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
        return False, False, False

    # Receive request_type, file_name & file_size. Terminate connection if malformed request_header
    try:
        request_type, file_name, file_size = request.split(SEPARATOR)
        file_size = int(file_size)
    except ValueError as vle:
        self.LOGGER.status_code(StatusCode.code[3000] + vle)
        STATUS_CODE = 3000
        STATUS_MESSAGE = vle
        send_status_ack(self, general_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
        return False, False, False

    return request_type, file_name, file_size


def send_status_ack(self, general_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE):
    """
    Sends a status acknowledgement message to the target machine (client/server)

    :param self: Client/Server Instance
    :param general_socket: Client/Server socket
    :param STATUS_CODE: Represents errors or success
    :param STATUS_MESSAGE: Detailed error information
    :param SEPARATOR: Separates the acknowledgement message
    :param HEADER_SIZE: Characters used to separate meaningful information from length of message

    :returns: None
    """

    try:
        message = f"{STATUS_CODE}{SEPARATOR}{STATUS_MESSAGE}"
        header = f"{len(message):<{HEADER_SIZE}}" + message
        general_socket.sendall(header.encode('utf-8'))
    except socket.error:
        self.LOGGER.status_code(StatusCode.code[3003])
        sys.exit(1)


def recv_status_ack(self, expected_status_code, SEPARATOR, HEADER_SIZE, previous_overflow=""):
    """
    Receives a status acknowledgement message from the target machine (client/server)

    :param expected_status_code: Status code to check against for logging
    :param self: Client/Server Instance
    :param SEPARATOR: Separates the acknowledgement message
    :param HEADER_SIZE: Characters used to separate meaningful information from length of message
    :param previous_overflow: Any previous overflow received from the previous recv() (if any)

    :returns: message_status, message_overflow
    """

    message_status, message_overflow = recv_message(self.socket, HEADER_SIZE, self.LOGGER, previous_overflow)
    if not message_status: return False, False

    status_code, status_message = message_status.split(SEPARATOR)
    if int(status_code) != expected_status_code:
        self.LOGGER.status_code(StatusCode.code[int(status_code)] + status_message)
        return False, False
    else:
        self.LOGGER.status_code(StatusCode.code[int(status_code)] + f"[{self.request}, {self.file}]")

    return message_status, message_overflow


def transfer_file(self):
    """
    Method for transferring file data to the targeted machine (client/server)

    :param self: Client/Server Instance

    :returns: True (if successful)
    """

    try:
        file_path = os.path.join("data", self.file)

        with open(file_path, 'rb') as file:
            while True:
                message = file.read(262144)
                if not message: break
                self.socket.sendall(message)
    except socket.error as soe:
        self.LOGGER.info(soe)
        return soe
    except Exception as exp:
        self.LOGGER.unknown_error(exp)
        return exp
    else:
        return True


def read_file(self, general_socket, file_name, file_size):
    """
    Method for reading the file data that is being transmitted by the target machine (client/server)

    :param self: Client/Server Instance
    :param general_socket: Client/Server socket
    :param file_name: Filename to read
    :param file_size: Size of the file to read

    :returns: True, True (if successful)
    """

    try:
        with open(os.path.join(self.data, file_name), "xb") as file:
            recv_bytes = 0
            while recv_bytes < file_size:
                file_data = general_socket.recv(262144)
                if not file_data: break
                file.write(file_data)
                recv_bytes += len(file_data)
    except socket.error as soe:
        self.LOGGER.info(soe)
        return False, soe
    except Exception as exp:
        self.LOGGER.unknown_error(exp)
        return False, exp
    else:
        return True, True


def send_listing(socket):
    """"""


def recv_listing(socket):
    """"""


def isFilePresent(file):
    return os.path.isfile(file)


def list_dirs(root_dir):
    for item in os.scandir(root_dir):
        print(item.name)
