import errno
import socket
import sys

from util import Logger


def get_client_arguments():
    """
    @:description Get information from client for connection setup, type of command and potentially a file

    @:returns CLIENT_HOST (str): The host of the client
    @:returns CLIENT_PORT (int): The port number of the client
    @:returns CLIENT_COMMAND (str): The type of action the user inputs
    @:returns CLIENT_FILE (str): The filename to download or upload (optional)
    """

    CLIENT_HOST = None
    CLIENT_PORT = None
    CLIENT_COMMAND = None
    CLIENT_FILE = None

    if len(sys.argv) >= 2:
        CLIENT_HOST = sys.argv[1]
    if len(sys.argv) >= 3:
        CLIENT_PORT = sys.argv[2]
    if len(sys.argv) >= 4:
        CLIENT_COMMAND = sys.argv[3]
    if len(sys.argv) >= 5:
        CLIENT_FILE = sys.argv[4]

    return CLIENT_HOST, CLIENT_PORT, CLIENT_COMMAND, CLIENT_FILE


def create_connection(CLIENT_HOST, CLIENT_PORT, LOGGER):
    """"""
    client_sock = None

    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((CLIENT_HOST, int(CLIENT_PORT)))
    except socket.error as soe:
        if soe.errno == errno.ECONNREFUSED:
            LOGGER.info(soe)
        sys.exit(1)
    finally:
        return client_sock


def file_transfer(client_sock):
    """"""

    received = True
    while received:
        input_message = input("Please enter the message that you want to send: ")

        if input_message == "EXIT":
            received = False
            client_sock.sendall(input_message.encode('utf-8'))
        else:
            client_sock.sendall(input_message.encode('utf-8'))
            request = client_sock.recv(1024)

            if request.decode('utf-8') == "EXIT":
                received = False
            else:
                print(request.decode('utf-8'))

    client_sock.close()


def main():
    """Main Method For Client"""

    CLIENT_HOST, CLIENT_PORT, CLIENT_COMMAND, CLIENT_FILE = get_client_arguments()
    LOGGER = Logger(CLIENT_HOST, CLIENT_PORT)

    client_sock = create_connection(CLIENT_HOST, CLIENT_PORT, LOGGER)
    file_transfer(client_sock)


if __name__ == "__main__":
    main()
