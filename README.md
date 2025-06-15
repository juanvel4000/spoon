
# 🥄 spoon
### (S)ophisticated (P)ackage (O)bject (O)btai(n)er

![GitHub License](https://img.shields.io/github/license/juanvel4000/spoon)

A **sophisticated** package manager for **Windows**, built for those who want a nice package manager with only the essentials.
## Installation

Bootstrap spoon using the powershell script

It will install `Python` if it is not installed

```pwsh
  irm https://spoon.juanvel400.xyz/install.ps1 | iex
```


## Manifests

spoon manifests are simple `json` files with a structure

A Manifest looks like
```json
{
	"name": "python",
	"version": "3.13.5",
	"url": "https://www.python.org/ftp/python/3.13.5/python-3.13.5-embed-amd64.zip",
	"sum": "md5:370a345dbea8bbc1830a2385f24632d2",
	"homepage": "https://python.org",
	"maintainer": {"name": "juanvel400"},
	"endpoints": {
		"python": "python.exe",
	},
	"type": "zip",
	"summary": "programming language"
}
```

It requires the following keys
- `name`: Name of the package
- `version`: Version of the package
- `summary`: A small description about the package
- `maintainer`: Whoever maintains the manifest
- `homepage`: A link to the homepage of the package
- `url`: The package itself, a link to the installer/zip
- `type`: The type of package. View available types below.
- `sum`: A sha256/md5 sum for authenticity (set to `skip:x` if none)

Other **optional** keys are
- `endpoints`: A dictionary of endpoints that point to a specific executable of the package
- `scripts`: pre/post install hooks written in powershell
### Types

Packages can have different types, the current (and only supported type) is 

- `zip`: A zip archive


## Ice Cream


An ice cream is a collection of manifests, it lets the user easily download manifests without having to write the full url

### Structure

- `INDEX.json`: Contains information about your ice cream, and a list of packages and their available versions
- `(package name)/`: Where the manifests go, these must be named after the version, (e.g: `v1.0.json`)

### INDEX.json
An `INDEX.json` must contain these keys
- `name`: The name of your ice cream, this is not the shortname defined by the user
- `maintainer`: The name of the person that maintains the ice cream
- `packages`: A list of packages and their available versions
- `description`: A short description about your ice cream

### `packages` list
The packages list is basically a json object with the names of the packages and each one is assigned an array with the available version
```json
"packages": {
    "python": ["3.13.5"]
}
```

### Example INDEX.json
```json
{
	"name": "main",
	"maintainer": "juanvel400",
	"description": "The main ice cream for spoon",
	"packages": {
		"python": ["3.13.5"]
	}
}
```
## License

**spoon** is licensed with MIT, read `LICENSE`
