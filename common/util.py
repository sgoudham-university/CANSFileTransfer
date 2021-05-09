import os
import socket
import sys

from common.status_code import StatusCode


def create_connection(host, port, local_machine, LOGGER):
    """
    Instantiates a connection for the given machine (Client/Server)

    :param host: Host of target machine
    :param port: Port of target machine
    :param local_machine: The machine creating the connection
    :param LOGGER: Logger to log information to the given local_machine
    :returns: general_socket
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
            LOGGER.info("Booting Server [...]")
            LOGGER.info("Server Online!")

        return general_socket


def recv_raw_message(general_socket, HEADER_SIZE, LOGGER):
    """
    Receive one message from Client/Server (without status message error handling)

    A "Fixed-Length Header" has been implemented to differentiate between messages sent
    E.g Format of Message '5                             Hello'
    '5' is the length of the actual message to be retrieved
    'Hello' is the content of the actual message (5 bytes)

    :param general_socket: Client/Server socket
    :param HEADER_SIZE: Characters used to separate meaningful information from length of message
    :param LOGGER: Logger to log information to the calling machine (Client/Server)
    :returns: complete_message, True (If successful)
    """

    complete_message = ""
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
                complete_message = complete_message[HEADER_SIZE:]
                break
    except socket.error as soe:
        LOGGER.info(soe)
        return False, soe
    except Exception as exp:
        LOGGER.unknown_error(exp)
        return False, exp
    else:
        return complete_message, True


def send_message(self, general_socket, message, HEADER_SIZE):
    """
    Send message to the targeted Client/Server

    :param general_socket: Client/Server socket
    :param message: Actual message to send to Client/Server
    :param self: Client instance
    :param HEADER_SIZE: Characters used to separate meaningful information from length of message
    :returns: True, True (if successful)
    """

    try:
        header = f"{len(message):<{HEADER_SIZE}}" + message
        general_socket.sendall(header.encode('utf-8'))
    except socket.error as soe:
        self.LOGGER.info(soe)
        return False, soe
    except Exception as exp:
        self.LOGGER.unknown_error(exp)
        return False, exp
    else:
        return True, True


def recv_message(self, general_socket, SEPARATOR, HEADER_SIZE):
    """
    Receive message from Client/Server.
    This implements functionality for sending status_ack back to the Client or Server should something go wrong

    :param self: Server Instance
    :param general_socket: Client/Server socket
    :param SEPARATOR: Characters to split the request by
    :param HEADER_SIZE: Characters used to separate meaningful information from length of message
    :returns: request (if successful)
    """

    request, status_msg = recv_raw_message(general_socket, HEADER_SIZE, self.LOGGER)
    if not request:
        STATUS_CODE = 3000
        STATUS_MESSAGE = status_msg
        send_status_ack(self, general_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE)
        return False

    return request


def send_status_ack(self, general_socket, STATUS_CODE, STATUS_MESSAGE, SEPARATOR, HEADER_SIZE):
    """
    Send a status acknowledgement message to the target machine (client/server)

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


def recv_status_ack(self, general_socket, expected_status_code, SEPARATOR, HEADER_SIZE):
    """
    Receive a status acknowledgement message from the target machine (client/server)

    :param general_socket: Client/Server socket
    :param expected_status_code: Status code to check against for logging
    :param self: Client/Server Instance
    :param SEPARATOR: Separates the acknowledgement message
    :param HEADER_SIZE: Characters used to separate meaningful information from length of message
    :returns: complete_status_message
    """

    complete_status_message, complete_status_message_status = recv_raw_message(general_socket, HEADER_SIZE, self.LOGGER)
    if not complete_status_message: return False

    status_code, status_message = complete_status_message.split(SEPARATOR)
    if int(status_code) != expected_status_code:
        self.LOGGER.status_code(StatusCode.code[int(status_code)] + status_message)
        return False

    message = f"[{self.request}, {self.file}]" if self.file else f"[{self.request}]"
    self.LOGGER.status_code(StatusCode.code[int(status_code)] + message)

    return complete_status_message


def transfer_file(self, general_socket, file_path, file_size):
    """
    Transfer file data to the targeted machine (client/server)

    :param general_socket: Client/Server socket
    :param file_path: Path to the file on the machine
    :param file_size: Filesize of the target file in bytes
    :param self: Client/Server Instance
    :returns: True, True (if successful)
    """

    try:
        file_bytes_sent = 0
        with open(file_path, 'rb') as file:
            while True:
                message = file.read(262144)
                if not message: break

                file_bytes_sent += len(message)
                progress_bar(self, file_bytes_sent, file_size, "Sending File")

                general_socket.sendall(message)
    except socket.error as soe:
        self.LOGGER.info(soe)
        return False, soe
    except Exception as exp:
        self.LOGGER.unknown_error(exp)
        return False, exp
    else:
        return True, True


def read_file(self, general_socket, file_name, file_size):
    """
   Read file data that is being transmitted by the target machine (client/server)

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

                recv_bytes += len(file_data)
                progress_bar(self, recv_bytes, file_size, "Reading File")

                file.write(file_data)
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


def progress_bar(self, count, total, status):
    """
    Shows visual progress of the file transfer in progress (sending and receiving)

    :param self:
    :param count:
    :param total:
    :param status:
    :returns: None
    """

    bar_len = 50
    filled_len = int(round(bar_len * count / float(total)))

    file_size_bytes = f"{count:,}/{total:,} Bytes"
    transfer_percent = round(100.0 * count / float(total), 2)
    file_bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write(f"[{self.LOGGER.host}:{self.LOGGER.port}] -> |{file_bar}| {file_size_bytes} | {transfer_percent}% | {status}...\r")
    sys.stdout.flush()

    if count >= total: print()


def is_file_present(file):
    """
    Determine if given file is present on the machine

    :param file: Given filename
    :returns: True/False
    """

    return os.path.isfile(file)


def get_dir(root_dir):
    """
    Return a dictionary containing all the items of a given root directory

    :param root_dir: The directory in which to search for files
    :returns: dir_dict
    """

    all_items_count = len([item for item in os.scandir(root_dir)])
    dir_string = ""
    file_count = 0

    for item in os.scandir(root_dir):
        dir_string += (item.name if file_count == all_items_count - 1 else item.name + "\n")
        file_count += 1

    return dir_string