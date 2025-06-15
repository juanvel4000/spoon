from spoon_install import *
from spoon_networking import *
from spoon_vars import *
from spoon_manifest import *
import urllib.request
from urllib.parse import urlparse
import json
def add(ice_cream, shortname):
    try:
        parsed = urlparse(ice_cream)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("invalid url")
        req = urllib.request.Request(
            ice_cream + '/INDEX.json',
            headers={"User-Agent": "spoon/0.2 (like uMIS/7)"}
        )


        with urllib.request.urlopen(req) as response:
            contents = response.read().decode("utf-8")
        c = json.loads(contents)
        pkgs = c['packages']
        index_path = os.path.join(ICECREAM_DIR, 'index.json')
        if os.path.exists(index_path):
            with open(index_path, 'r') as ic:
                found_icecream = json.load(ic)
        else:
            found_icecream = {}
       
        for name, versions in pkgs.items():
            if name not in found_icecream:
                found_icecream[name] = {"versions": versions, "icecream": shortname}
            else:
               for ver in versions:
                    if ver not in found_icecream[name]["versions"]:
                        found_icecream[name]["versions"].append(ver)

        with open(os.path.join(ICECREAM_DIR, 'index.json'), 'w') as ic:
            json.dump(found_icecream, ic, indent=2)
        known_path = os.path.join(ICECREAM_DIR, 'known_icecreams')
        entry = f'{shortname}@{ice_cream}\n'
        if os.path.exists(known_path):
            with open(known_path, 'r') as kn:
                if entry in kn.readlines():
                    return True
        with open(known_path, 'a') as kn:
            kn.write(entry)
        return True

    except Exception as e:
        print(f"* error: {e}")


def resolve_package(name, version=None):
    try:
        index = os.path.join(ICECREAM_DIR, 'index.json')
        known = os.path.join(ICECREAM_DIR, 'known_icecreams')

        if not os.path.exists(known):
            raise FileNotFoundError(f"{known} does not exist, please add an ice cream first")
        if not os.path.exists(index):
            raise FileNotFoundError(f"{index} does not exist, please add an ice cream first")
        with open(index, 'r') as i:
            packages = json.load(i)
        known_icecreams = {}
        with open(known, 'r') as k:
            for line in k:
                if '@' in line:
                    s, u = line.strip().split('@', 1)
                    known_icecreams[s] = u

        if name not in packages:
            raise ValueError(f"* {name} not found in index")

        pkgd = packages[name]
        versions, icecream = pkgd['versions'], pkgd['icecream']

        if version is None:
            version = versions[-1]

        if version not in versions:
            raise ValueError(f"version {version} not found for package {name}")

        if icecream not in known_icecreams:
            raise ValueError(f"no known ice cream to resolve '{icecream}'")
        return {
                "url": known_icecreams[icecream],
                "name": name,
                "version": version,
                "icecream": icecream,
                "full_resolv": f"{known_icecreams[icecream]}/{name}/{version}.json"
                }

    except Exception as e:
        print(f"* error: {e}")
        return False


