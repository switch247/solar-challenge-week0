param(
    [switch]$SkipInstall
)

Write-Host "== run_tests.ps1 -> Create venv (if missing), install deps (unless skipped), and run pytest =="

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment .venv..."
    python -m venv .venv
}

# Activate the venv for the current session
Write-Host "Activating .venv..."
. .\.venv\Scripts\Activate.ps1

if (-not $SkipInstall) {
    Write-Host "Installing requirements from requirements.txt (this may take a while)..."
    pip install -r requirements.txt
}

Write-Host "Running pytest..."
pytest -q

exit $LASTEXITCODE
