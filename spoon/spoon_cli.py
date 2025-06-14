from spoon_install import *
from spoon_vars import *
from spoon_manifest import *
import sys
import os
def _help():
    print("sophisticated package object obtainer (spoon)")
    print(f"version {VERSION}")
    print("doctor               -       Check the status of the lockfile")
    print("lint <manifest>      -       Check for syntax errors in a package manifest")
    print("help                 -       Show this message")
    print("remove <packages>    -       Remove a package")
    print("spoon is licensed with the MIT license")
    sys.exit(0)
def main():
    args = sys.argv[1:] # remove filename
    argc = len(args) # get arg count
    if argc == 0:
        _help()
    cmd, opts = args[0], args[1:]
    match cmd:
        case 'list':
            ents = listEntries()
            if ents == []:
                print("* no packages installed")
            else:
                print("* installed packages")
                for i in ents:
                    pkg, ver = i['name'], i['version']
                    print(f"* {pkg}@{ver}")
        case 'install':
            if argc == 1:
                print("usage: install <manifest(s)...>")
                sys.exit(1)
            for pkg in opts:
                if os.path.isfile(pkg):
                    if check_file(pkg):
                        install_manifest(pkg)

        case 'remove':
            if argc == 1:
                print("usage: remove <package(s)>")
                sys.exit(1)
            for pkg in opts:
                remove_package(pkg)
        case 'doctor':
            print("* validating lockfile")
            checkLockfile()
        case 'lint':
            if argc == 1:
                print("usage: lint <manifest>")
                sys.exit(1)
            fil = opts[0]
            if not os.path.isfile(fil):
                print(f"* file {fil} does not exist")
                sys.exit(1)
            print(f"* linting {fil}")
            if check_file(fil):
                print("* manifest is valid")
            else:
                print("* invalid manifest")


        case 'help':
            _help()
        case _:
            print(f"* unknown command: {cmd}")
            sys.exit(1)
if __name__ == "__main__":
    main()
