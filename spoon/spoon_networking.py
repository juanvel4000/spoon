import urllib.request
from spoon_manifest import *
from spoon_vars import *
from urllib.parse import urlparse
import tempfile
import sys
def parseurl(url):
    try:
        urlparse(url)

        if url.endswith('.json'):
            return True
        return False
    except Exception as e:
        print(f"* error: {e}")

def download_manifest(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"spoon {VERSION} (Python {sys.version})"}
    )
    out = tempfile.mktemp()
    print(f"* downloading manifest from {url}")
    with urllib.request.urlopen(req) as response, open(out, 'wb') as o:
        total_size = int(response.getheader('Content-Length', 0))
        block_size = 8192
        count = 0

        while True:
            chunk = response.read(block_size)
            if not chunk:
                break
            o.write(chunk)
            count += 1
            progress_bar(count, block_size, total_size)
    print("")
    return out
