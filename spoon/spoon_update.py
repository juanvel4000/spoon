from spoon_install import *
from spoon_manifest import *
from spoon_networking import *
from spoon_440 import *
from spoon_vars import *
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

