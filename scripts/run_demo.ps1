Write-Host "== run_demo.ps1 -> Generate sample data and start Streamlit =="

if (-not (Test-Path .venv)) {
    Write-Host ".venv not found. Creating..."
    python -m venv .venv
}

# Activate venv
. .\.venv\Scripts\Activate.ps1

Write-Host "Creating sample CSVs in scripts/..."
python .\scripts\generate_sample_data.py --outdir .\scripts

Write-Host "Starting Streamlit (open http://localhost:8501)"
streamlit run src/main.py --server.port=8501
