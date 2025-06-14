# spoon_manifest: check if the manifest is valid
import json
def check_file(fil):
    with open(fil, 'r') as f:
        return check_contents(f.read())
def check_contents(jso: str):
    try:
        dic = json.loads(jso)
    except json.JSONDecodeError as e:
        raise ValueError(f"json error: {e}")
    for i in ["name", "summary", "sum", "type"]:
        if not isinstance(i, str):
            raise ValueError(f"{i} is not a string")
        if i not in dic:
            raise ValueError(f"could not find required key {i} in the requested manifest")

    if "url" not in dic:
        # assume that is a script
        if dic['type'] != "script":
            raise TypeError("url not found and type is not a script")
        else:
            if 'scripts' not in dic:
                raise TypeError(f"type is scripts but no scripts found")
            else:
                if 'core' not in dic:
                    raise TypeError(f"type is scripts but core not in scripts")

    return True

