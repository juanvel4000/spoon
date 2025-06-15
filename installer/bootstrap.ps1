if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Error "your PowerShell version is too old"
    exit
}

if ($env:OS -ne "Windows_NT" -or -not (Get-Command curl -ErrorAction SilentlyContinue)) {
    Write-Error "curl not found or OS not supported"
    exit
}
function Is-PythonInstalled {
    try {
        $version = & py --version 2>&1
        if ($version -match "Python 3\.13\.5") {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}
Write-Output @"
* * * * * * * * *
* Sophisticated *
* Package       * 
* Object        *
* Obtai-        * 
* Ner           *
* * * * * * * * *
* Installer     *
* * * * * * * * *
"@
if (Is-PythonInstalled) {
	Write-Output "* found python"
} else {
	Write-Output "* installing python 3.13.5"
	curl -o python-installer.exe https://www.python.org/ftp/python/3.13.5/python-3.13.5-amd64.exe
	Start-Process .\python-installer.exe -ArgumentList '/quiet', 'InstallAllUsers=0', 'PrependPath=1', 'Include_test=0' -Wait
	Remove-Item python-installer.exe
}
Write-Output "* creating .spoon directories"
$spoonRoot = "$env:USERPROFILE\.spoon"
$spoonBin  = "$spoonRoot\bin"
$spoonCode = "$spoonRoot\Spoon"

New-Item -ItemType Directory -Path $spoonRoot -Force > $null
New-Item -ItemType Directory -Path $spoonBin -Force > $null
New-Item -ItemType Directory -Path $spoonCode -Force > $null

Write-Output "* downloading spoon"
curl -o "$spoonRoot\spoon.zip" https://github.com/juanvel4000/spoon/archive/refs/heads/main.zip
Expand-Archive -Path "$spoonRoot\spoon.zip" -DestinationPath "$spoonCode" -Force
Remove-Item "$spoonRoot\spoon.zip"

Write-Output "* creating a launcher"
@"
@echo off
py ""$spoonCode\spoon-main\spoon\spoon_cli.py"" %*
"@ | Set-Content -Path "$spoonBin\spoon.cmd" -Encoding ASCII

Write-Output "* adding .spoon/bin to PATH"
$oldPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $oldPath.Contains($spoonBin)) {
    $newPath = "$oldPath;$spoonBin"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
}

Write-Output "* spoon has been installed!"
Write-Output "* please restart your terminal to use the spoon command"
