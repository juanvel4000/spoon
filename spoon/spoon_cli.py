from spoon_install import *
from spoon_vars import *
from spoon_manifest import *
from spoon_networking import *
from icecream import *
from spoon_update import *
import sys
import os
import time
def _help():
    print("sophisticated package object obtainer (spoon)")
    print(f"version {VERSION}")
    print("doctor                       -       Check the status of the lockfile")
    print("lint <manifest>              -       Check for syntax errors in a package manifest")
    print("help                         -       Show this message")
    print("remove <packages>            -       Remove a package")
    print("list                         -       List installed packages")
    print("search <package>             -       Search for a package in available ice creams")
    print("icecream add <name> <url>    -       Add a new ice cream")
    print("install <package>            -       Install a package from a manifest file, ice cream or manifest url")
    print("spoon is licensed with the MIT license")
    sys.exit(0)
def main():
    args = sys.argv[1:] # remove filename
    argc = len(args) # get arg count
    if argc == 0:
        _help()
    cmd, opts = args[0], args[1:]
    match cmd:
        case 'check-updates':
            pkgs = getpackagestoupdate()
            print("* updateable packages")
            for pkg in pkgs['updateable']:
                print(f" * {pkg}")
            print("* up-to-date packages")
            for pkg in pkgs['non-updateable']:
                print(f" * {pkg}")
        case 'icecream':
            if argc == 1:
                print("usage: icecream <command> ...")
                sys.exit(1)
            acmd = opts[0]
            match acmd:
                case 'add':
                    if argc == 2:
                        print("usage: icecream add <name> <url>")
                        sys.exit(1)
                    if argc == 3:
                        print(f"usage: icecream add {opts[1]} <url>")
                        sys.exit(1)
                    name, url = opts[1], opts[2]
                    add(url, name)
                case _:
                    _help()
        case 'search':
            if argc == 1:
                print("usage: search <package(s)...>")
                sys.exit(1)
            print("┌found:")
            starttime = int(time.time())
            for pkg in opts:
                if '@' in pkg:
                    name, version = pkg.split('@')
                else:
                    name = pkg
                    version = None
                r = resolve_package(name, version)
                if r:
                    print(f"├{r['name']}@{r['version']} on {r['icecream']}")
            print(f"└on {int(time.time()) - starttime}s")
        case 'list':
            ents = listEntries()
            if ents == []:
                print("* no packages installed")
            else:
                print("┌installed packages")
                for i in ents:
                    pkg, ver = i['name'], i['version']
                    print(f"├ {pkg}@{ver}")
                print("└yes")
        case 'install':
            if argc == 1:
                print("usage: install <manifest(s)...>")
                sys.exit(1)
            for pkg in opts:
                if os.path.isfile(pkg):
                    # is a file
                    if check_file(pkg):
                        install_manifest(pkg)
                else:
                    # is a url to a manifest
                    if not parseurl(pkg):
                        # is a icecream entry
                        if '@' in pkg:
                            name, version = pkg.split('@')
                        else:
                            name = pkg

                            version = None
                        netpkg = resolve_package(name, version)   
                        if netpkg:
                            p = download_manifest(netpkg['full_resolv'])
                            install_manifest(p)
                            sys.exit(1)
                        else:
                            # neither
                            print(f"* package not found {pkg}")
                            sys.exit(1)
                    m = download_manifest(pkg)
                    if m:
                        install_manifest(m)
                    else:
                        print(f"* package is an url but no manifest was downloaded")
                        sys.exit(1)

        case 'remove':
            if argc == 1:
                print("usage: remove <package(s)>")
                sys.exit(1)
            for pkg in opts:
                remove_package(pkg)
        case 'doctor':
            print("* validating lockfile")
            checkLockfile()
            print("* backing up lockfile")
            backupCurrentLock()
            print("* success, your spoon is healthy")
        case 'backup':
            print("* backing up lock...")
            backupCurrentLock()
            print("* lock backed up")
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
