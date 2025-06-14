from spoon_install import *
from spoon_vars import *
from spoon_manifest import *
import sys
import os
def _help():
    print("sophisticated package object obtainer (spoon)")
    print(f"version {VERSION}")
    print("spoon is licensed with the MIT license")
def main():
    args = sys.argv[1:] # remove filename
    argc = len(args) # get arg count
    if argc == 0:
        _help()
if __name__ == "__main__":
    main()
