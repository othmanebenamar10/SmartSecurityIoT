# Smart Security IoT (Python Desktop)

This folder contains the Python/PySide6 desktop implementation. It is the app launched by `run_app.ps1` and packaged by the build scripts.

Quick start (dev):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH="app"
python -m smart_security_iot
```

Build:

```powershell
.\app\build_exe.ps1
.\app\build_installer.ps1
```

Configuration:
- Use environment variables or `.env` at repo root (see `.env.example`).
- Secrets are never hardcoded.
