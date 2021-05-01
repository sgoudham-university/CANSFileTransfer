import sys

sys.path.append('..')
from util import Logger, create_connection


class Server:
    def __init__(self):
        self.HOST = ""
        self.PORT = None
        self.COMMAND = None
        self.FILE = None
        self.SOCKET = None
        self.LOGGER = None

        self.get_arguments()

        self.LOGGER = Logger(self.HOST, self.PORT)
        self.SOCKET = create_connection(self.HOST, self.PORT, "server", "client", self.LOGGER)

    def get_arguments(self):
        """"""

        if len(sys.argv) >= 2:
            self.PORT = sys.argv[1]

    def handle(self):
        """"""

        while True:
            received = True
            cli_sock, cli_addr = self.SOCKET.accept()

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
    server = Server()
    server.handle()


if __name__ == "__main__":
    main()
