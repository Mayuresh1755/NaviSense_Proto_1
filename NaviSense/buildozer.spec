[app]
title = NaviSense
package.name = navisense
package.domain = org.navisense
source.dir = .
source.include_exts = py,kv,png,jpg,json,onnx,txt,md
source.exclude_dirs = .git,tests,__pycache__,.venv,venv
version = 0.1.0
requirements = python3,kivy,numpy,opencv,plyer
orientation = portrait
fullscreen = 0
android.permissions = CAMERA,RECORD_AUDIO
android.api = 35
android.minapi = 26
android.archs = arm64-v8a
android.allow_backup = False
android.private_storage = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
