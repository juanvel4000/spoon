from spoon_install import *
from spoon_vars import *
from spoon_manifest import *
from spoon_networking import *
from icecream import *
from spoon_update import *
import sys
import os
import time
import shutil
import ctypes
import subprocess
import platform
import json
def dump_sample_manifest(out):
    with open(out + '.json', 'w') as js:
        json.dump({
            "name": "sample",
            "version": "0.1",
            "maintainer": {"name": "johndoe"},
            "url": "https://ftp.example.com/sample/v0.1/sample-v0.1-x86_64-windows-msvc.zip",
            "type": "zip",
            "sum": "sha256:...",
            "summary": "sample...",
            "endpoints": {"sample": "sample/sample.exe"},
            "homepage": "https://example.com/sample.html",

            }, js, indent=2)
    check_file(out + '.json')
def is_20h2_or_newer():
    version = platform.version()
    build_number = int(version.split('.')[2])
    return build_number >= 19042
if not is_20h2_or_newer():
    print("* please update to Windows 10 20H2 (Build 19042, October 2020 Update) or Higher")
    sys.exit(1)
def is_elevated():
    return ctypes.windll.shell32.IsUserAnAdmin() != 0

if is_elevated():
    print("* please run spoon on a regular shell (no admin/uac)")
    sys.exit(1)
def list_symlinks(pkg):
    entry = getLockEntry(pkg)
    if not entry:
        print("* package is not installed")
        return False

    version = entry['version']
    symlist_path = os.path.join(SYMLISTDIR, f"{pkg}-{version}")
    if not os.path.isfile(symlist_path):
        print(f"* package does not have a symlist")
        return False

    with open(symlist_path, 'r') as f:
        lines = f.readlines()

    print(f"* {pkg}@{version}:")
    for line in lines:
        src, dst = line.strip().split('=>')
        full_src = os.path.normpath(os.path.join(PKG_DIR, pkg, src.strip()))
        full_dst = os.path.normpath(os.path.join(BIN_DIR, dst.strip()))

        relative_src = os.path.relpath(full_src, os.path.dirname(full_dst))
        print(f" *  {dst.strip()} -> {relative_src}")


                    
def dumplock(out):
    print("* reading current lock")
    with open(LOCKFILE, 'r') as lock:
        l = lock.read()
    print(f"* dumping to {out}")
    with open(out, 'w') as ou:
        ou.write(l)
    print("* done!")
def loadlock(fil):
    print(f"* checking if {fil} is a valid lock")
    if checkLockfile(fil):
        print(f"* loading {fil} as lock")
        print("* backing up current lock...")
        backupCurrentLock()
        print("* looking for differences beetween locks")
        with open(fil, 'r') as l:
            newlock = json.load(l)
        with open(LOCKFILE, 'r') as lo:
            oldlock = json.load(lo)
        setpkgs, not_inlock, newpkgs, oldpkgs = [], [], [], []

        for pkg in oldlock['packages']:
            oldpkgs.append({"name": pkg['name'], "version": pkg['version']})

        for pkg in newlock['packages']:
            newpkgs.append({"name": pkg['name'], "version": pkg['version']})


        for a in newpkgs:
            for b in oldpkgs:
                if a['name'] == b['name']:
                    setpkgs.append({"name": b['name']})

        for a in oldpkgs:
            if not any(a['name'] == b['name'] for b in setpkgs):
                not_inlock.append(a['name'])
        if not_inlock != []:
            print(f"* {" ".join(not_inlock)}")
            conf = input(f"* the packages above will be removed, do you want to proceed? [y/N]")
            if conf in ['y', 'Y']:
                for pkg in not_inlock:
                    remove_package(pkg)
            else:
                print("* cannot proceed")
                return False
        os.remove(LOCKFILE)
        shutil.copy(fil, LOCKFILE)
        sync = input("* done. do you want to sync the lock? [Y/n]: ")
        if sync in ['N', 'n']:
            return True
        else:
            if synclock():
               print("* lock synchronized successfully")
               return True
    
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
    print("check-updates                -       Check for available package updates")
    print("update                       -       Update all the packages")
    print("install <package>            -       Install a package from a manifest file, ice cream or manifest url")
    print("sync-lock                    -       Synchronize packages in the lock")
    print("dump-lock <output>           -       Dump the current lock to <output>")
    print("load-lock <file>             -       Load <file> as a lock")
    print("refresh                      -       Update the index")
    print("get-paths                    -       Get the paths used by spoon")
    print("links <package>              -       List all the symlinks of a package")
    print("init <file>                  -       Dump a sample manifest to <file>")
    print("spoon is licensed with the MIT license")
    sys.exit(0)
def main():
    args = sys.argv[1:] # remove filename
    argc = len(args) # get arg count
    if argc == 0:
        _help()
    cmd, opts = args[0], args[1:]
    match cmd:
        case 'init':
            if argc == 1:
                print("usage: init <file>")
                sys.exit(1)
            dump_sample_manifest(opts[0])
        case 'links':
            if argc == 1:
                print("usage: links <package>")
                sys.exit(1)
            list_symlinks(opts[0])
            sys.exit(0)
        case 'refresh':
            dryRun = False
            if '--dry-run' in opts:
                dryRun = True
            update_index(dryRun)
        case 'get-paths':
            starttime = int(time.time())
            print("┌ Paths")
            for i in [SPOON_DIR, BIN_DIR, PKG_DIR, ICECREAM_DIR, SYMLISTDIR, LOCK_BACKUPDIR]:
                print(f"├ {i}")
            print(f"└ on {int(time.time()) - starttime}s")
        case 'dump-lock':
            if argc == 1:
                print("usage: dump-lock <output>")
                sys.exit(1)
            dumplock(opts[0])
        case 'load-lock':
            if argc == 1:
                print("usage: load-lock <file>")
                sys.exit(1)
            loadlock(opts[0])
        case 'update':
            pkgs = getpackagestoupdate()
            autoyes = False
            if '-y' in opts:
                autoyes = True
            updateallpackages(pkgs['updateable'], autoyes)
        case 'sync-lock':
            autoyes = False
            if '-y' in opts:
                autoyes = True
            synclock(autoyes)
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
            reinstall = False
            if '--force' in opts:
                opts.remove('--force')
                reinstall = True
            for pkg in opts:
                if os.path.isfile(pkg):
                    # is a file
                    if check_file(pkg):
                        install_manifest(pkg, reinstall)
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
                            install_manifest(p, reinstall)
                            sys.exit(1)
                        else:
                            # neither
                            print(f"* package not found {pkg}")
                            sys.exit(1)
                    m = download_manifest(pkg)
                    if m:
                        install_manifest(m, reinstall)
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
