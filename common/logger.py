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

        self.host = host
        self.port = port

    def info(self, logger_string):
        """
        Print out to the console

        :param logger_string: Specifies string to print out to console
        :returns: None
        """

        print(f"[{self.host}:{self.port}] -> [INFO] {logger_string}")

    def print_dir(self, dir_dict):
        """
        Print out the contents of the provided directory dictionary

        :param dir_dict: Dictionary that has the following key:value pairs - {item_name: item_type}
        :returns None
        """

        for item_name, item_type in dir_dict.items():
            spaces = 2 if item_type == "[DIR]" else 1
            print(f"[{self.host}:{self.port}] ->   {item_type}{' ':>{spaces}}---> {item_name}")

    def status_code(self, code):
        """
        Print out to the console with given custom error code/description

        :param code: Custom error code with description
        :returns: None
        """

        print(f"[{self.host}:{self.port}] -> {code}")

    def unknown_error(self, exception):
        """
        Print out unknown exception to the console

        :param exception: Type of exception that occurred
        :returns: None
        """

        print(f"[{self.host}:{self.port}] -> Unknown Exception Occurred: {exception}")
