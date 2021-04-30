import os
from socket import socket, AF_INET, SOCK_STREAM
import sys

SERVER_HOST = ""
SERVER_PORT = int(sys.argv[1])

server_sock = socket(AF_INET, SOCK_STREAM)
server_sock.bind((SERVER_HOST, SERVER_PORT))
server_sock.listen(5)

def list_dirs(root_dir):
    for item in os.scandir(root_dir):
        if item.is_dir():
            list_dirs(item)
        print(item.name)


def list_files(root_dir):
    SPACE = ' '
    INDENT_SPACES = 4

    for root, dirs, files in os.walk(root_dir):
        level = root.replace(root_dir, '', 1).count(os.sep)
        indent = SPACE * INDENT_SPACES * level
        sub_indent = SPACE * INDENT_SPACES * (level + 1)

        print_file(indent, os.path.basename(root) + "/")
        for file in files:
            print_file(sub_indent, file)


def print_file(indentation_level, file_name):
    print(f"{indentation_level}{file_name}")


rootdir = os.path.join("data")
list_dirs(rootdir)
list_files(rootdir)
