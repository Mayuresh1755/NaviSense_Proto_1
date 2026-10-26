# NaviSense — Laptop + Android source (no BAT files)

This project includes a laptop webcam prototype, manual pinhole distance estimation, calibration utility, tests, Android/Kivy source, and the supplied YOLO11n weights.

**Important:** This is source code, not a prebuilt APK. The Android project still needs to be built with Buildozer under Linux/WSL2, then tested on the target phone. No one can guarantee zero errors without running it on your exact PC and phone; this package avoids Windows `.bat` files and gives copy/paste commands instead.

## Windows laptop setup (PowerShell, no BAT files)

Use Python **3.11 or 3.12**. Open PowerShell in the extracted `NaviSense` folder. If the folder is `C:\NaviSense`, run:

```powershell
cd C:\NaviSense
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-laptop.txt
.\.venv\Scripts\python.exe main.py
```

These commands do not activate the virtual environment and do not require changing PowerShell's execution policy. If `py -3.11` is not found, install Python 3.11 from python.org and enable the Python Launcher during installation, or replace `py -3.11` with the full path to your Python 3.11 executable.

If installation fails, copy the **first complete error** from PowerShell. Do not install packages into Python 3.14 for this project unless you have confirmed all dependencies support it.

### Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### Calibrate manual distance estimation

Put a person fully in frame at a measured distance (for example 2 metres), then run:

```powershell
.\.venv\Scripts\python.exe calibrate_distance.py --object person --distance 2.0
```

Follow the on-screen prompt to capture calibration. The known height is approximate; recalibrate for the actual camera and keep the output in mind as an estimate, not an exact measurement.

## Export the ONNX model for Android

Run these commands from the project root after laptop dependencies are installed:

```powershell
.\.venv\Scripts\python.exe scripts\export_onnx.py
.\.venv\Scripts\python.exe scripts\stage_android_model.py
```

Model export may download/export supporting components and requires adequate disk space and internet access for any missing packages.

## Android APK build

The Android source is in `android_app/`. Buildozer is not supported as a native Windows build workflow; use Ubuntu or WSL2. Copy the project into the Linux filesystem, install Java 17, Buildozer and required system packages, then from `android_app/` run:

```bash
buildozer android debug
```

See `android_app/BUILD_ANDROID.md` and `android_app/buildozer.spec`. The first build downloads Android SDK/NDK and Python-for-Android dependencies and may take considerable time and disk space. Camera access, model output compatibility, inference speed, and speech must be validated on the actual phone. An APK is not included because this environment has not built and tested one.

## Distance estimation

The estimator uses `distance_m = focal_length_px * assumed_real_height_m / bounding_box_height_px`. Accuracy depends on calibration, actual object size, pose, occlusion, and detection quality. Unknown object sizes should remain unknown rather than inventing a distance.

## Safety

NaviSense is a research prototype, not a certified mobility aid. Test in a controlled environment with a sighted assistant. Do not rely on it as the sole means of avoiding obstacles.
