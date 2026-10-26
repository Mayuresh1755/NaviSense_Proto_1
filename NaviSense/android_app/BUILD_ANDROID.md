# Build Android APK

1. On Windows, in the project root, run `install_windows.bat`, then `export_onnx_windows.bat`. The second command stages the exported ONNX model into this folder.
2. Copy this entire `android_app` folder into the WSL2/Linux home directory.
3. Install Java 17, Buildozer and the Linux build dependencies described in the root `README.md`.
4. In this folder, run `buildozer android debug`.
5. Install the generated `bin/*.apk` on a test phone and validate camera access, object detection, distance estimation, audio and memory use before relying on it.

The Android build has not been executed in the environment where this source package was created. Buildozer/OpenCV recipe and camera-provider compatibility must be verified rather than assumed.
