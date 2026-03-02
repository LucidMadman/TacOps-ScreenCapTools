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

# ensure pyinstaller is available in the Python environment
try {
    & python -m pip show PyInstaller >$null 2>&1
} catch {
    # pip itself might not be available? fall through to install
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller not found in current environment, installing..."
    & python -m pip install --upgrade pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install PyInstaller. Please install it manually and re-run the build."
        exit 1
    }
}

Write-Host "Building $exeName.exe..."

# Use the python executable from the current environment to run PyInstaller
# because the venv's Scripts directory might not be on the PATH. Building the
# argument list explicitly ensures PowerShell calls 'python' with '-m'
$pyCmd = "python"

# assemble arguments for the module invocation and other flags
$psArgs = @(
    '-m', 'PyInstaller',
    '--onefile',
    '--windowed',
    "--name", $exeName,
    '--distpath', 'dist',
    '--specpath', 'build',
    'tacops_gui.py'
)

& $pyCmd @psArgs

if ($LASTEXITCODE -eq 0) {
    $exePath = "dist\$exeName.exe"
    Write-Host "Build successful: $exePath"
} else {
    Write-Host "Build failed"
    exit 1
}
