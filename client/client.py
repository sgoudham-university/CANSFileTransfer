import sys

sys.path.append('..')
from util import Logger, create_connection


class Client:
    def __init__(self):
        self.HOST = None
        self.PORT = None
        self.COMMAND = None
        self.FILE = None
        self.SOCKET = None
        self.LOGGER = None

        self.get_arguments()

        self.LOGGER = Logger(self.HOST, self.PORT)
        self.SOCKET = create_connection(self.HOST, self.PORT, "client", "server", self.LOGGER)

    def get_arguments(self):
        """
        Get information from user for connection setup, type of command and potentially a file
        """

        if len(sys.argv) >= 2:
            self.HOST = sys.argv[1]
        if len(sys.argv) >= 3:
            self.PORT = sys.argv[2]
        if len(sys.argv) >= 4:
            self.COMMAND = sys.argv[3]
        if len(sys.argv) >= 5:
            self.FILE = sys.argv[4]

    def handle(self):
        """"""

        received = True
        while received:
            input_message = input("Please enter the message that you want to send: ")

            if input_message == "EXIT":
                received = False
                self.SOCKET.sendall(input_message.encode('utf-8'))
            else:
                self.SOCKET.sendall(input_message.encode('utf-8'))
                request = self.SOCKET.recv(1024)

                if request.decode('utf-8') == "EXIT":
                    received = False
                else:
                    print(request.decode('utf-8'))

        self.SOCKET.close()


def main():
    client = Client()
    client.handle()


if __name__ == "__main__":
    main()
