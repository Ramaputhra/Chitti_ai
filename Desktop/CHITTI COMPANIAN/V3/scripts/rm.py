import shutil
import os

target = "desktop/capabilities/sys_file_open"
if os.path.exists(target):
    shutil.rmtree(target)
    print("Deleted")
else:
    print("Does not exist")
