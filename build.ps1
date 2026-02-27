# Build script for tacops_gui
# Usage: .\build.ps1 -Version "1.0.0"
# Output: dist\tacops_gui_v1.0.0.exe

param(
    [Parameter(Mandatory=$true)]
    [string]$Version
)

if (-not (Test-Path ".venv") -and -not (Test-Path "venv")) {
    Write-Host "Error: Virtual environment not found. Activate it first."
    exit 1
}

$exeName = "TacopsScreenCapTools_v$Version"
Write-Host "Building $exeName.exe..."

pyinstaller `
    --onefile `
    --windowed `
    --name $exeName `
    --distpath dist `
    --specpath build `
    tacops_gui.py

if ($LASTEXITCODE -eq 0) {
    $exePath = "dist\$exeName.exe"
    Write-Host "Build successful: $exePath"
} else {
    Write-Host "Build failed"
    exit 1
}
