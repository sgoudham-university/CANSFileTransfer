import errno
import socket
import sys

sys.path.append('..')
from util import Logger


def get_server_arguments():
    """"""

    SERVER_HOST = ""
    SERVER_PORT = None

    if len(sys.argv) >= 2:
        SERVER_PORT = sys.argv[1]

    return SERVER_HOST, SERVER_PORT


def create_connection(SERVER_HOST, SERVER_PORT, LOGGER):
    """"""
    server_sock = None

    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((SERVER_HOST, int(SERVER_PORT)))
        server_sock.listen(5)
    except socket.error as soe:
        if soe.errno == errno.ECONNREFUSED:
            LOGGER.info(soe)
        sys.exit(1)
    finally:
        return server_sock


def file_transfer(server_sock):
    """"""
    SERVER_COMMAND = None
    SERVER_FILE = None

    while True:
        received = True
        cli_sock, cli_addr = server_sock.accept()

        while received:
            request = cli_sock.recv(1024)

            if request.decode('utf-8') == "EXIT":
                received = False
            else:
                print(request.decode('utf-8'))

                input_message = input("Please enter the message that you want to send: ")

                if input_message == "EXIT":
                    received = False
                cli_sock.sendall(input_message.encode('utf-8'))

        cli_sock.close()


def main():
    """Main Method For Client"""

    SERVER_HOST, SERVER_PORT = get_server_arguments()
    LOGGER = Logger(SERVER_HOST, SERVER_PORT)

    server_sock = create_connection(SERVER_HOST, SERVER_PORT, LOGGER)
    file_transfer(server_sock)


if __name__ == "__main__":
    main()
