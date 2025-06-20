# spoon_vars: basic variables, functions and lock manipulation
import os
import sys
import json
import time
import shutil
SPOON_DIR = os.path.join(os.path.expanduser('~'), '.spoon')
BIN_DIR = os.path.join(SPOON_DIR, 'bin')
PKG_DIR = os.path.join(SPOON_DIR, 'packages')
LOCKFILE = os.path.join(SPOON_DIR, 'spoon-lock.json')
LOCK_BACKUPDIR = os.path.join(SPOON_DIR, 'locks-backup')
SYMLISTDIR = os.path.join(SPOON_DIR, 'symlist')
ICECREAM_DIR = os.path.join(SPOON_DIR, 'icecream')
VERSION = "v0.6"
for d in [SPOON_DIR, BIN_DIR, PKG_DIR, LOCK_BACKUPDIR, SYMLISTDIR, ICECREAM_DIR]:
	os.makedirs(d, exist_ok=True)
def symlist_add(listn, src, dst):
    with open(os.path.join(SYMLISTDIR, listn), 'a') as l:
        l.write(f'{src}=>{dst}\n')
def backupCurrentLock(): # this should be called only by the frontend
    shutil.copy(LOCKFILE, os.path.join(LOCK_BACKUPDIR, f'lock-{int(time.time())}.json'))

def progress_bar(count, block_size, total_size):
    bar_length = 40
    if total_size == 0:
        downloaded_kb = count * block_size / 1024
        sys.stdout.write(f"\r[{'=' * bar_length}] ({downloaded_kb:.2f} KB)")
        sys.stdout.flush()
        return

    percent = min(count * block_size / total_size, 1.0)
    arrow = '=' * max(int(round(percent * bar_length) - 1), 0) + '>'
    spaces = '-' * (bar_length - len(arrow))
    sys.stdout.write(f"\r[{arrow + spaces}] {int(percent * 100)}%")
    sys.stdout.flush()

def symlink(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    with open(dst, 'w') as f:
        f.write(f'@echo off\n"{src}" %*\n')
class LockfileError(Exception):
    pass
if not os.path.isfile(LOCKFILE):
    with open(LOCKFILE, 'w') as lock:
        json.dump({"packages": []}, lock, indent=2)
def checkLockfile(fil=LOCKFILE):
    if not os.path.isfile(fil):
        raise LockfileError('lockfile does not exist')
    with open(fil, 'r') as lock:
        cl = json.load(lock)
    if 'packages' not in cl:
        return False
    for pkg in cl['packages']:
        for i in ['name', 'version', 'installed_at']:
            if i not in pkg:
                return False
    return True
def addLockEntry(package, version, dryRun=False): # adds a entry to the lock, supports dry run
    if os.path.isfile(LOCKFILE):
        with open(LOCKFILE, 'r') as lock:
            cl = json.load(lock)
    else:
        cl = {"packages": []}
    cl['packages'] = [p for p in cl['packages'] if p['name'] != package]
    cl['packages'].append({"name": package, "version": version, "installed_at": int(time.time())})
    if dryRun:
        print(f"[dry-run] lockfile updated with {package}, {version}")
        return cl
    else:
        with open(LOCKFILE, 'w') as lock:
            json.dump(cl, lock, indent=2)
    return cl

def getLockEntry(package):
    if not os.path.isfile(LOCKFILE):
        return False
    with open(LOCKFILE, 'r') as lock:
        cl = json.load(lock)
    for p in cl.get('packages', []):
        if p['name'] == package:
            return p
    return False

def removeLockEntry(package, dryRun=False):
    if not os.path.isfile(LOCKFILE):
        return False
    with open(LOCKFILE, 'r') as lock:
        cl = json.load(lock)
    if all(p['name'] != package for p in cl['packages']):
        return False
    
    cl['packages'] = [p for p in cl['packages'] if p['name'] != package]
    if dryRun:
        return cl
    with open(LOCKFILE, 'w') as lock:
        json.dump(cl, lock, indent=2)
    return cl
def lockExists():
    return os.path.isfile(LOCKFILE)
def listEntries():
    if not os.path.isfile(LOCKFILE):
        return []
    with open(LOCKFILE, 'r') as lock:
        cl = json.load(lock)
    return cl.get('packages', [])
