import os
import socket
import sys


def create_connection(HOST, PORT, LOCAL_MACHINE, LOGGER):
    """

    :param HOST:
    :param PORT:
    :param LOCAL_MACHINE:
    :param LOGGER:
    :returns:
    """

    try:
        general_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        general_socket.settimeout(100)

        if LOCAL_MACHINE == "client":
            general_socket.connect((HOST, int(PORT)))
        elif LOCAL_MACHINE == "server":
            general_socket.bind((HOST, int(PORT)))
            general_socket.listen(5)

    except socket.error as soe:
        LOGGER.info(soe)
        sys.exit(1)
    except Exception as exp:
        LOGGER.unknown_error(exp)
        sys.exit(1)
    else:
        if LOCAL_MACHINE == "client":
            LOGGER.info(f"Successfully Connected to [{HOST}:{PORT}]")
        elif LOCAL_MACHINE == "server":
            LOGGER.info(f"Booting Server [...]")
            LOGGER.info(f"Server Online!")

        return general_socket


def recv_message(gen_socket, HEADER_SIZE, LOGGER, previous_overflow=""):
    """"""

    complete_header = ""
    complete_header += previous_overflow
    current_overflow = previous_overflow
    message_length = 0
    incoming_message = True

    try:
        while True:
            request = gen_socket.recv(32768)
            if not request: break

            complete_header += request.decode("utf-8")

            if incoming_message:
                message_length = int(complete_header[:HEADER_SIZE])
                incoming_message = False

            if len(complete_header) - HEADER_SIZE >= message_length:
                header_with_overflow = complete_header[HEADER_SIZE:]
                complete_header = header_with_overflow[:message_length]
                current_overflow = header_with_overflow[message_length:]
                break
    except socket.error as soe:
        LOGGER.info(soe)
        return False, soe
    except Exception as exp:
        LOGGER.unknown_error(exp)
        return False, exp
    else:
        LOGGER.info(f"Header Received! [{', '.join(complete_header.split())}]")
        return complete_header, current_overflow


def send_header(self, general_socket):
    """"""


def send_file(self, file_path, HEADER_SIZE, SEPARATOR):
    """"""


def recv_file(self, general_socket, file_name, HEADER_SIZE):
    """"""


def send_listing(socket):
    """"""


def recv_listing(socket):
    """"""


def transfer_file(self, SEPARATOR, HEADER_SIZE):
    """"""

    try:
        file_path = os.path.join("data", self.FILE)

        message = f"{self.COMMAND}{SEPARATOR}{self.FILE}"
        header = f"{len(message):<{HEADER_SIZE}}" + message

        self.SOCKET.sendall(header.encode('utf-8'))

        with open(file_path, 'rb') as file:
            while True:
                message = file.read(65536)
                if not message: break
                header = f"{len(message):<{HEADER_SIZE}}" + message.decode('utf-8')
                self.SOCKET.sendall(header.encode('utf-8'))
    except socket.error as soe:
        self.LOGGER.info(soe)
        return soe
    except Exception as exp:
        self.LOGGER.unknown_error(exp)
        return exp
    else:
        return True


def read_file(self, general_socket, file_name, overflow, HEADER_SIZE):
    """"""

    try:
        with open(os.path.join(self.DATA, file_name), "xb") as file:
            while True:
                file_data, new_overflow = recv_message(general_socket, HEADER_SIZE, self.LOGGER, overflow)
                if not file_data: break
                file.write(file_data.encode('utf-8'))
                overflow = new_overflow
    except socket.error as soe:
        self.LOGGER.info(soe)
        return soe
    except Exception as exp:
        self.LOGGER.unknown_error(exp)
        return exp
    else:
        return True


def isValidFile(file):
    return os.path.isfile(file)


def list_dirs(root_dir):
    for item in os.scandir(root_dir):
        print(item.name)
