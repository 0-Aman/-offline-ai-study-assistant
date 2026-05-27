$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Streamlit = Join-Path $Root ".venv\Scripts\streamlit.exe"

if (-not (Test-Path $Python)) {
    Write-Host "Creating virtual environment..."
    python -m venv (Join-Path $Root ".venv")
}

Write-Host "Installing dependencies..."
& $Python -m pip install -r (Join-Path $Root "requirements.txt")

Write-Host "Starting FastAPI backend at http://127.0.0.1:8000"
Start-Process -FilePath $Python -ArgumentList @(
    "-m",
    "uvicorn",
    "app.backend.main:app",
    "--reload",
    "--host",
    "127.0.0.1",
    "--port",
    "8000"
) -WorkingDirectory $Root

Write-Host "Starting Streamlit frontend at http://127.0.0.1:8501"
Start-Process -FilePath $Streamlit -ArgumentList @(
    "run",
    "app/frontend/streamlit_app.py",
    "--server.address",
    "127.0.0.1",
    "--server.port",
    "8501"
) -WorkingDirectory $Root

Write-Host "App is starting. Open http://127.0.0.1:8501"
