# spoon_440: utilities to work with version parsing acording to PEP440
import re

_precedence = {'dev': -1, 'a': 0, 'b': 1, 'rc': 2, '': 3, 'post': 4}

def parse_version(v):
    v = v.lower().strip()
    match = re.match(r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:(a|b|rc|dev|post)(\d+))?$', v)
    if not match:
        raise ValueError(f"Invalid version: {v}")
    major, minor, patch, stage, stage_ver = match.groups()
    return (
        int(major),
        int(minor or 0),
        int(patch or 0),
        _precedence.get(stage or '', 5),
        int(stage_ver or 0)
    )

def compare_versions(a, b):
    return parse_version(a) < parse_version(b)

