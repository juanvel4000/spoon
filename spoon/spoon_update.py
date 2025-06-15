from spoon_install import *
from spoon_manifest import *
from spoon_networking import *
from spoon_440 import *
from spoon_vars import *
from icecream import *
import json
def getpackagestoupdate():
    with open(LOCKFILE, 'r') as lock:
        cl = json.load(lock)
    with open(os.path.join(ICECREAM_DIR, 'index.json'), 'r') as ind:
        index = json.load(ind)
    nonupdateable = []
    updateable = []
    for pkg in cl['packages']:
        name, version = pkg['name'], pkg['version']
        if name not in index:
            nonupdateable.append(name)
            continue
        else:
            vers = index[name]['versions']
            updable = False
            for ver in vers:
                if compare_versions(version, ver):
                    updateable.append({name: ver})
                    updable = True
                    break
            if not updable:
                nonupdateable.append(name)
                
    return {
        "non-updateable": nonupdateable, 
        "updateable": updateable
    }
def updateallpackages(updateable, autoyes=False):
    for pkg in updateable:
        for name, version in pkg.items():
            if autoyes == False:
                res = input(f"* update {name} to {version}? [y/N]: ")
                if res in ['y', 'Y']:
                    pass
                else:
                    print(f"* skipping package: {name} ")
                    break

            net = resolve_package(name, version)
            if not net:
                print("* error: package not found in any ice cream")
                break
            n = download_manifest(net['full_resolv'])
            install_manifest(n)
            break

        continue

def synclock(autoyes=True):
    with open(LOCKFILE, 'r') as lock:
        l = json.load(lock)
        
    for pkg in l['packages']:
        name, version = pkg['name'], pkg['version']
        if autoyes == False:
            res = input(f"* install {name} at {version}? [y/N]: ")
            if res not in ['y', 'Y']:
                print(f"* skipping package: {name} ")
                continue

        net = resolve_package(name, version)
        if not net:
            print("* error: package not found in any ice cream")
            continue
        n = download_manifest(net['full_resolv'])
        install_manifest(n, True)
    return True

