import zipfile
import sys
import json
import urllib.request as req
from spoon_vars import *
from spoon_manifest import check_file
import os
import shutil
import time
import hashlib

def progress_bar(count, block_size, total_size):
    bar_length = 40
    if total_size == 0:
        downloaded_kb = count * block_size / 1024
        sys.stdout.write(f"\r[{'=' * bar_length}] ({downloaded_kb:.2f} KB)")
        sys.stdout.flush()
        return

    percent = min(count * block_size / total_size, 1.0)
    arrow = '=' * max(int(round(percent * bar_length) - 1), 0) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    sys.stdout.write(f"\r[{arrow + spaces}] {int(percent * 100)}%")
    sys.stdout.flush()

def verify_sum(fil, ssum):
    alg, hhash = ssum.split(':')
    hasher = getattr(hashlib, alg)()
    with open(fil, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest() == hhash

def install_manifest(manifest):
    starttime = int(time.time())
    print("* validating manifest")
    if not check_file(manifest):
        return False
    print("* validating lockfile")
    if not checkLockfile():
        raise LockfileError("error with the lockfile")
    with open(manifest, 'r') as man:
        manif =  json.load(man)
    print(f"* installing {manif['name']}@{manif['version']}")
    if manif['type'] not in ["zip", "exe-static", "msi"]:
        print("* fatal: package is not a zip, msi or exe-static")
        return False
    ex = os.path.join(PKG_DIR, manif['name'])
    os.makedirs(ex, exist_ok=True)
    dl = os.path.join(ex, f"{manif['name']}-{manif['version']}.spoon-pkg")
    print(f"* downloading {manif['url']}...")
    req.urlretrieve(manif['url'], dl, reporthook=progress_bar)
    print("\n", end="")
    if manif['sum'] != "skip:x":
        if verify_sum(dl, manif['sum']):
            print("* sum is valid")
        else:
            print("* sum is not valid")
            os.remove(dl)
            sys.exit(1)
    if manif['type'] == "zip":
        if not zipfile.is_zipfile(dl):
            print("this is not a zip file")
            return False
        with zipfile.ZipFile(dl, 'r') as zf:
            zf.extractall(ex)
    elif manif['type'] == "exe-static":
        shutil.copy(dl, os.path.join(ex, f"{manif['name']}.exe"))
    elif manif['type'] == "msi":
        newdl = os.path.join(ex, f"{manif['name']}-{manif['version']}.msi")
        os.rename(dl, newdl)
        print(f"* installing {os.path.basename(newdl)}...")
        args = manif.get("installer_args", "").replace("%TARGETDIR%", ex)
        install_cmd = f'msiexec /i "{newdl}" /quiet /norestart {args}'
        result = os.system(install_cmd)
    # make symlinks
    if 'endpoints' in manif:
        for endp, rel_path in manif['endpoints'].items():
            dst = os.path.join(BIN_DIR, endp + '.bat')  
            src = os.path.join(PKG_DIR, manif['name'], rel_path)  
            if not os.path.isfile(src):
                print(f"* warning: file {src} does not exist")
                continue
            print(f"* creating link {endp}")
            symlink(src, dst)
            symlist_add(f"{manif['name']}-{manif['version']}", src, dst)
    print("* adding to lockfile")
    addLockEntry(manif['name'], manif['version'])
    print(f"* done! installed {manif['name']} in {int(time.time()) - starttime}s")
    return True
def remove_package(name):
    starttime = int(time.time())
    if not getLockEntry(name):
        return False
    ver = getLockEntry(name)['version']
    print(f"* removing {name}@{ver}")
    shutil.rmtree(os.path.join(PKG_DIR, name))
    with open(os.path.join(SYMLISTDIR, f"{name}-{ver}"), 'r') as l:
        for sym in l.readlines():
            dst = sym.strip().split('=>')[1]
            print(f"* removing link {os.path.basename(dst).removesuffix('.bat')}")
            os.remove(os.path.join(BIN_DIR, dst))
    os.remove(os.path.join(SYMLISTDIR, f"{name}-{ver}"))
    if removeLockEntry(name):
        print(f"* done! removed {name} in {int(time.time()) - starttime}s")
        return True
