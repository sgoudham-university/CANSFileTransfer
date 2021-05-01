import os
import socket
import sys


class Logger:
    """
    A class representing a Logger which logs information to the client and server
    """

    def __init__(self, host, port):
        """
        Constructor for Logger
        :param host: Given host from User
        :param port: Given port from User
        """

        self.connection = f"[{host}:{port}]"

    def info(self, logger_string):
        """
        : Print out to the console
        :param logger_string: Specifies string to print out to console
        :returns: None
        """

        print(f"{self.connection} -> {logger_string}")


class Command:
    """Specify constants for client actions on given server"""

    GET = "get"
    PUT = "put"
    LIST = "list"


def create_connection(HOST, PORT, LOCAL_MACHINE, TARGET_MACHINE, LOGGER):
    """

    :param HOST:
    :param PORT:
    :param LOCAL_MACHINE:
    :param TARGET_MACHINE:
    :param LOGGER:
    :return:
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
        LOGGER.info(f"Unknown Exception: {exp}")
        sys.exit(1)

    return general_socket


def send_file(socket, file_name):
    """"""


def recv_file(socket, file_name):
    """"""


def send_listing(socket):
    """"""


def recv_listing(socket):
    """"""


def list_dirs(root_dir):
    for item in os.scandir(root_dir):
        print(item.name)
#
#
# root_dir = os.path.join("server", "data")
# list_dirs(root_dir)
