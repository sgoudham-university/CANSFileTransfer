class StatusCode:
    code = {
        1000: "[CustomErrno 1000] Arguments Are Missing! E.g [python client.py <host> <port> <put file_name | get file_name | list>]",
        1001: "[CustomErrno 1001] Given Command Not Recognised! Terminating Client [...]",
        1002: "[CustomErrno 1002] Given File Not Found! Terminating Client [...]",

        2000: "[CustomErrno 2000] Timed Out - Terminating Server [...]",
        2001: "Listening For Client Connections [...]",
        2002: "[CustomErrno 2002] Arguments Are Missing! E.g [python server.py <port>]",

        3000: "[CustomErrno 3000] File Transfer Failure: ",

        4000: "[CustomSucc 4000] File Transferred Successfully!"
    }
