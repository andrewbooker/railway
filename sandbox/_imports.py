
import sys
import os
parentDir = os.path.dirname(os.getcwd())
if "railway" not in parentDir:
    print("needs to run in sandbox")
    exit()

sys.path.append(parentDir)