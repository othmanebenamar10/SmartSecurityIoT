$ErrorActionPreference = "Stop"

$AppName = "Smart Security IoT"
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\SmartSecurityIoT"
$ZipPath = Join-Path $PSScriptRoot "SmartSecurityIoT.zip"

if (-not (Test-Path $ZipPath)) {
  throw "Missing package: $ZipPath"
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Expand-Archive -Path $ZipPath -DestinationPath $InstallDir -Force

$ExePath = Join-Path $InstallDir "SmartSecurityIoT.exe"
if (-not (Test-Path $ExePath)) {
  throw "Application executable not found after install: $ExePath"
}

$ProgramsDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$StartShortcut = Join-Path $ProgramsDir "$AppName.lnk"
$DesktopShortcut = Join-Path ([Environment]::GetFolderPath("DesktopDirectory")) "$AppName.lnk"

$Shell = New-Object -ComObject WScript.Shell
foreach ($ShortcutPath in @($StartShortcut, $DesktopShortcut)) {
  $Shortcut = $Shell.CreateShortcut($ShortcutPath)
  $Shortcut.TargetPath = $ExePath
  $Shortcut.WorkingDirectory = $InstallDir
  $Shortcut.Description = $AppName
  $Shortcut.IconLocation = $ExePath
  $Shortcut.Save()
}

Start-Process -FilePath $ExePath -WorkingDirectory $InstallDir
