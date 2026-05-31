param(
  [string]$VenvPath = ".venv"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

if (-not (Test-Path $VenvPath)) {
  python -m venv $VenvPath
}

& "$VenvPath\Scripts\pip.exe" install -r requirements.txt
& "$VenvPath\Scripts\pip.exe" install pyinstaller

& "$VenvPath\Scripts\pyinstaller.exe" --noconfirm --clean --name "SmartSecurityIoT" `
  --windowed `
  --paths "app" `
  --collect-data "cv2" `
  --hidden-import "bcrypt" `
  --hidden-import "requests" `
  --hidden-import "pymodbus.client" `
  --hidden-import "plyer" `
  --hidden-import "face_recognition" `
  --hidden-import "face_recognition_models" `
  --hidden-import "deepface" `
  app\smart_security_iot\__main__.py

Write-Host "Built: dist\SmartSecurityIoT\SmartSecurityIoT.exe"
