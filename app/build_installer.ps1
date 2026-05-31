param(
  [string]$VenvPath = ".venv"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

& (Join-Path $PSScriptRoot "build_exe.ps1") -VenvPath $VenvPath

$DistApp = Join-Path $RepoRoot "dist\SmartSecurityIoT"
$InstallerWork = Join-Path $RepoRoot "dist\installer"
$ZipPath = Join-Path $InstallerWork "SmartSecurityIoT.zip"
$SetupExe = Join-Path $RepoRoot "dist\SmartSecurityIoT-Setup.exe"
$SedPath = Join-Path $InstallerWork "SmartSecurityIoT.SED"

if (-not (Test-Path $DistApp)) {
  throw "Missing build output: $DistApp"
}

New-Item -ItemType Directory -Force -Path $InstallerWork | Out-Null
if (Test-Path $ZipPath) {
  Remove-Item -LiteralPath $ZipPath -Force
}

Compress-Archive -Path (Join-Path $DistApp "*") -DestinationPath $ZipPath -Force
Copy-Item -LiteralPath "installer\install.ps1" -Destination $InstallerWork -Force
Copy-Item -LiteralPath "installer\setup.bat" -Destination $InstallerWork -Force

$Sed = @"
[Version]
Class=IEXPRESS
SEDVersion=3

[Options]
PackagePurpose=InstallApp
ExtractOnly=0
ShowInstallProgramWindow=0
HideExtractAnimation=1
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=%InstallPrompt%
DisplayLicense=%DisplayLicense%
FinishMessage=%FinishMessage%
TargetName=%TargetName%
FriendlyName=%FriendlyName%
AppLaunched=%AppLaunched%
PostInstallCmd=%PostInstallCmd%
AdminQuietInstCmd=%AppLaunched%
UserQuietInstCmd=%AppLaunched%
SourceFiles=SourceFiles

[SourceFiles]
SourceFiles0=$InstallerWork\

[SourceFiles0]
%FILE0%=
%FILE1%=
%FILE2%=

[Strings]
InstallPrompt=
DisplayLicense=
FinishMessage=Smart Security IoT installed.
TargetName=$SetupExe
FriendlyName=Smart Security IoT
AppLaunched=setup.bat
PostInstallCmd=<None>
FILE0=SmartSecurityIoT.zip
FILE1=install.ps1
FILE2=setup.bat
"@

Set-Content -LiteralPath $SedPath -Value $Sed -Encoding ASCII
& "$env:WINDIR\System32\iexpress.exe" /N /Q $SedPath

Write-Host "Installer built: $SetupExe"
