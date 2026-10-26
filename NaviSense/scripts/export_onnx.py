"""Export the included YOLO11n weights to ONNX for Android OpenCV DNN."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import config
from ultralytics import YOLO
def main():
 if not config.MODEL_PT.exists():raise FileNotFoundError(config.MODEL_PT)
 result=YOLO(str(config.MODEL_PT)).export(format='onnx',imgsz=config.INFERENCE_SIZE,dynamic=False,simplify=False,opset=12)
 out=Path(result)
 if out.resolve()!=config.MODEL_ONNX.resolve():out.replace(config.MODEL_ONNX)
 print(f'ONNX export created: {config.MODEL_ONNX} ({config.MODEL_ONNX.stat().st_size/1048576:.1f} MiB)')
if __name__=='__main__':main()
