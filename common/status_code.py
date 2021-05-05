class StatusCode:
    """
    This class contains a dictionary mapping of all the status codes within the program, they are classed as follows:

    1000 -> Status Codes for the Client
    2000 -> Status Codes for the Server
    3000 -> Error Codes shared between the Client & Server
    4000 -> Success Status Codes shared between the Client & Server
    """

    code = {
        1000: "[CustomErrno 1000]: Arguments Are Missing! E.g [python client.py <host> <port> <put file_name | get file_name | list>]",
        1001: "[CustomErrno 1001]: Given Command Not Recognised! Terminating Client [...]",
        1002: "[CustomErrno 1002]: Given File Already Exists On Specified Server! Terminating Client [...]",

        2000: "[CustomErrno 2000]: Timed Out - Terminating Server [...]",
        2001: "Listening For Client Connections [...]",
        2002: "[CustomErrno 2002]: Arguments Are Missing! E.g [python server.py <port>]",

        3000: "Malformed File Header: ",
        3001: "[CustomErrno 3001]: File Transfer Failure: ",
        3003: "[CustomErrno 3003]: Could Not Send Status To Client!",

        4000: "[CustomSucc 4000]: File Header Received Properly: ",
        4001: "[CustomSucc 4001]: Request Successful: "
    }
