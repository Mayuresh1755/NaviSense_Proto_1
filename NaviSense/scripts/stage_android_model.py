from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1];src=root/'models'/'yolo11n.onnx';dst=root/'android_app'/'models'/'yolo11n.onnx'
if not src.is_file():raise SystemExit(f'Missing {src}; run `python scripts/export_onnx.py` first.')
dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);print(f'Staged model: {dst}')
