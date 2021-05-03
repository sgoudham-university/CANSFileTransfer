class Error:
    ONE = "[Errno-1] Arguments are Missing! E.g [python client.py <HOST> <PORT> <REQUEST> | python client.py <HOST> <PORT> <REQUEST> <FILE>]"
    TWO = "[Errno-2] Given Command Not Recognised! Exiting Client [...]"
    THREE = "[Errno-3] Given File Not Found! Exiting Client [...]"
    FOUR = "[Errno-4] Timed Out - No Client Connection Received - Exiting Server [...]"
    FIVE = " [Errno-5] File Transfer Failure! Terminating Connection [...]"
    SIX = ""


class Success:
    ONE = "[Succ-1] File Transferred Successfully!"
