import zipfile
import sys
import json
import urllib.request as req
from spoon_vars import *
from spoon_manifest import check_file
import os
import shutil
def progress_bar(count, block_size, total_size):
    percent = min(count * block_size / total_size, 1.0)
    bar_length = 40
    arrow = '=' * int(round(percent * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    sys.stdout.write(f"\r[{arrow + spaces}] {int(percent * 100)}%")
    sys.stdout.flush()
def install_manifest(manifest):
    print("* validating manifest")
    if not check_file(manifest):
        return False
    print("* validating lockfile")
    if not checkLockfile():
        raise LockfileError("error with the lockfile")
    with open(manifest, 'r') as man:
        manif =  json.load(man)
    print(f"* installing {manif['name']}@{manif['version']}")
    if manif['type'] != "zip":
        return False # only zip is supported for now
    ex = os.path.join(PKG_DIR, manif['name'])
    os.makedirs(ex, exist_ok=True)
    dl = os.path.join(ex, f"{manif['name']}-{manif['version']}.spoon.zip")
    print(f"* downloading {manif['url']}...")
    req.urlretrieve(manif['url'], dl, reporthook=progress_bar)
    print("\n", end="")
    if not zipfile.is_zipfile(dl):
        return False
    with zipfile.ZipFile(dl, 'r') as zf:
        zf.extractall(ex)
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
    return True
def remove_package(name):
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
        print(f"* successfully removed {name}")
        return True
