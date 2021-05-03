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
        Print out to the console
        :param logger_string: Specifies string to print out to console
        :returns: None
        """

        print(f"{self.connection} -> {logger_string}")

    def status_code(self, code):
        """
        Print out to the console with given custom error code/description
        :param code: Custom error code with description
        :returns: None
        """

        print(f"{self.connection} -> {code}")

    def unknown_error(self, exception):
        """
        Print out unknown exception to the console
        :param exception: Type of exception that occurred
        :returns: None
        """

        print(f"{self.connection} -> Unknown Exception Occurred: {exception}")
