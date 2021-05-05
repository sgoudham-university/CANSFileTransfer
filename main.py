import filecmp
import os

filecmp.clear_cache()
print(filecmp.cmp(os.path.join("client", "data", "1GB.txt"), os.path.join("server", "data", "1GB.txt")))
print(filecmp.cmp(os.path.join("client", "data", "empty_file.txt"), os.path.join("server", "data", "empty_file.txt")))
print(filecmp.cmp(os.path.join("client", "data", "lorem_ipsum.txt"), os.path.join("server", "data", "lorem_ipsum.txt")))
print(filecmp.cmp(os.path.join("client", "data", "1GB.txt"), os.path.join("server", "data", "1GB.txt")))
print(filecmp.cmp(os.path.join("client", "data", "100MB.bin"), os.path.join("server", "data", "100MB.bin")))
