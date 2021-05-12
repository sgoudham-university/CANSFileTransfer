class StatusCode:
    """
    This class contains a dictionary mapping of all the status codes within the program, they are classed as follows:

    1000 -> Status Codes for the Client

    2000 -> Status Codes for the Server

    3000 -> Error Codes shared between the Client & Server

    4000 -> Success Status Codes shared between the Client & Server
    """

    code = {
        1000: "[ERROR 1000]: Arguments Are Missing! E.g [python client.py <host> <port> <put file_name | get file_name | list>]",
        1001: "[ERROR 1001]: Given Command Not Recognised! Terminating Client [...]",

        2000: "[ERROR 2000]: Timed Out - Terminating Server [...]",
        2001: "Listening For Client Connections [...]",
        2002: "[ERROR 2002]: Arguments Are Missing! E.g [python server.py <port>]",

        3000: "Malformed Request Message: ",
        3001: "[ERROR 3001]: File Transfer Failure: ",
        3002: "[ERROR 3002]: Directory Transfer Failure: ",
        3003: "[ERROR 3003]: Could Not Send Status To Client!",
        3004: "[ERROR 3004]: Given File Does Not Exist On Server! Terminating Connection [...]",
        3005: "[ERROR 3005]: Given File Already Exists On Server! Terminating Connection [...]",
        3006: "[ERROR 3006]: Given File Does Not Exist On Client Machine! Terminating Connection [...]",
        3007: "[ERROR 3007]: Given File Already Exists On Client Machine! Terminating Connection [...]",

        4000: "[SUCCESS 4000]: Request Type Received Properly: ",
        4001: "[SUCCESS 4001]: File Information Sent Successfully: ",
        4002: "[SUCCESS 4002]: Request Successful: ",
        4003: "[SUCCESS 4003]: Ready For File Transfer: ",
        4004: "[SUCCESS 4004]: Client Ready To Receive File",
        4005: "[SUCCESS 4005]: Client File Exists: ",
        4006: "[SUCCESS 4006]: Client Received Server Directory Size Successfully: ",
        4007: "[SUCCESS 4007]: Client Ready To Receive Server Directory Size: ",
        4008: "[SUCCESS 4008]: Server Ready To Receive File Information: "
    }
