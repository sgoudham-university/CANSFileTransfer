import os


def list_dirs(root_dir):
    for item in os.scandir(root_dir):
        print(item.path)
        if item.is_dir():
            list_dirs(item)


rootdir = os.path.join("data")
list_dirs(rootdir)