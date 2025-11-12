param(
    [int]$Port = 8501
)

Write-Host "== start_streamlit.ps1 -> Activate venv and start Streamlit on port $Port =="

if (-not (Test-Path ".venv")) {
    Write-Host ".venv not found. Creating..."
    python -m venv .venv
}

Write-Host "Activating .venv..."
. .\.venv\Scripts\Activate.ps1

Write-Host "Starting Streamlit app (app/main.py) on port $Port..."
streamlit run app/main.py --server.port=$Port
