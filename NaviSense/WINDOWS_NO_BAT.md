# Windows setup without BAT files

Open PowerShell in the extracted project directory and run one command at a time:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-laptop.txt
.\.venv\Scripts\python.exe main.py
```

No environment activation is needed, and these commands do not require changing PowerShell execution policy. See `README.md` for troubleshooting, tests, calibration, ONNX export, and Android packaging.
