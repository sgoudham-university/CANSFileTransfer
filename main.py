import filecmp
import os

filecmp.clear_cache()
print(filecmp.cmp(os.path.join("client", "data", "1GB.txt"), os.path.join("server", "data", "1GB.txt")))
