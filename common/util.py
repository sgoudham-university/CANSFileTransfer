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
        LOGGER.error(exp)
        sys.exit(1)
    else:
        if LOCAL_MACHINE == "client":
            LOGGER.info(f"Connection Success to [{HOST}:{PORT}]")
        elif LOCAL_MACHINE == "server":
            LOGGER.info(f"Establishing Server Connection [...]")
            LOGGER.info(f"Connection Established!")
        return general_socket


def recv_header(gen_socket, HEADER_SIZE, LOGGER):
    """"""

    complete_header = ""
    overflow = ""
    message_length = 0
    incoming_message = True

    try:
        while not len(complete_header) - HEADER_SIZE == message_length:
            request = gen_socket.recv(48)
            if not request: break

            if incoming_message:
                message_length = int(request[:HEADER_SIZE])
                incoming_message = False
            complete_header += request.decode("utf-8")

            if len(complete_header) - HEADER_SIZE >= message_length:
                header_with_overflow = complete_header[HEADER_SIZE:]
                complete_header = header_with_overflow[:message_length]
                overflow = header_with_overflow[message_length:]
                break

            if len(complete_header) - HEADER_SIZE == message_length:
                print(complete_header[HEADER_SIZE:])
                incoming_message = True
    except socket.error as soe:
        LOGGER.info(soe)
        return False
    except Exception as exp:
        LOGGER.error(exp)
        return False
    else:
        LOGGER.info(f"Header Received! [{', '.join(complete_header.split())}]")
        return complete_header, overflow


def recv_message(gen_socket, HEADER_SIZE, OVERFLOW, LOGGER):
    """"""

    complete_header = ""
    overflow = OVERFLOW
    complete_header += OVERFLOW
    message_length = 0
    incoming_message = True

    try:
        counter = 1
        while not len(complete_header) - HEADER_SIZE == message_length:
            request = gen_socket.recv(48)
            if not request: break

            if incoming_message:
                if not overflow: message_length = int(request[:HEADER_SIZE])
                incoming_message = False

            complete_header += request.decode("utf-8")
            if counter == 1: message_length = int(complete_header[:HEADER_SIZE])

            if len(complete_header) - HEADER_SIZE > message_length:
                header_with_overflow = complete_header[HEADER_SIZE:]
                complete_header = header_with_overflow[:message_length]
                overflow = header_with_overflow[message_length:]

            if len(complete_header) - HEADER_SIZE == message_length:
                print(complete_header[HEADER_SIZE:])
                incoming_message = True
            counter = counter + 1

    except socket.error as soe:
        LOGGER.info(soe)
        return False
    except Exception as exp:
        LOGGER.error(exp)
        return False
    else:
        LOGGER.info(f"Header Received! [{', '.join(complete_header[HEADER_SIZE:].split())}]")
        return complete_header[HEADER_SIZE:].encode('utf-8'), overflow


def send_header(socket, HEADER_SIZE):
    """"""


def send_file(socket, file_name):
    """"""


def recv_file(socket, file_name):
    """"""


def send_listing(socket):
    """"""


def recv_listing(socket):
    """"""


def isValidFile(file):
    return os.path.isfile(file)


def list_dirs(root_dir):
    for item in os.scandir(root_dir):
        print(item.name)
