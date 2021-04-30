import os


class Logger:
    def __init__(self, host, port):
        self.connection = f"[{host}:{port}]"

    def info(self, logger_string):
        print(f"{self.connection} -> {logger_string}")


class Command:
    """Specify constants for client actions on given server"""

    GET = "get"
    PUT = "put"
    LIST = "list"


# def list_dirs(root_dir):
#     for item in os.scandir(root_dir):
#         print(item.name)
#
#
# root_dir = os.path.join("server", "data")
# list_dirs(root_dir)
