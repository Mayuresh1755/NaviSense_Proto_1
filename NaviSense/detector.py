"""YOLO11n detector: Ultralytics on laptop, ONNX/OpenCV DNN on Android."""
from dataclasses import dataclass
import os,sys
import cv2,numpy as np
import config
from distance_calculator import DistanceCalculator
from direction import get_direction
COCO_NAMES=['person','bicycle','car','motorcycle','airplane','bus','train','truck','boat','traffic light','fire hydrant','stop sign','parking meter','bench','bird','cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack','umbrella','handbag','tie','suitcase','frisbee','skis','snowboard','sports ball','kite','baseball bat','baseball glove','skateboard','surfboard','tennis racket','bottle','wine glass','cup','fork','knife','spoon','bowl','banana','apple','sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair','couch','potted plant','bed','dining table','toilet','tv','laptop','mouse','remote','keyboard','cell phone','microwave','oven','toaster','sink','refrigerator','book','clock','vase','scissors','teddy bear','hair drier','toothbrush']
@dataclass
class Detection:
 name:str; confidence:float; bbox:tuple; center:tuple; direction:str; distance:float|None; category:str
class NaviDetector:
 def __init__(self,backend='auto'):
  self.distance=DistanceCalculator(); self.backend=backend; self.model=None; self.net=None
  android=sys.platform=='android' or 'ANDROID_ARGUMENT' in os.environ
  if backend=='onnx' or (backend=='auto' and android):
   if not config.MODEL_ONNX.exists(): raise FileNotFoundError(f'Missing {config.MODEL_ONNX}; export ONNX on the laptop first')
   self.net=cv2.dnn.readNetFromONNX(str(config.MODEL_ONNX)); self.backend='onnx'
  else:
   if not config.MODEL_PT.exists(): raise FileNotFoundError(f'Missing model: {config.MODEL_PT}')
   try: from ultralytics import YOLO
   except ImportError as e: raise RuntimeError('Ultralytics missing. Run install_windows.bat first.') from e
   self.model=YOLO(str(config.MODEL_PT)); self.backend='ultralytics'
 def detect(self,frame):
  if frame is None or not hasattr(frame,'shape') or frame.size==0:return []
  h,w=frame.shape[:2]
  if (self.distance.frame_width,self.distance.frame_height)!=(w,h):self.distance.configure_camera(w,h)
  raw=[]
  if self.backend=='ultralytics':
   result=self.model.predict(frame,imgsz=config.INFERENCE_SIZE,conf=config.CONFIDENCE_THRESHOLD,verbose=False,device='cpu')[0]
   for b in result.boxes:
    box=tuple(map(float,b.xyxy[0].tolist())); cls=int(b.cls[0]); name=result.names.get(cls,str(cls)) if isinstance(result.names,dict) else result.names[cls]
    raw.append((str(name),float(b.conf[0]),box))
  else: raw=self._detect_onnx(frame)
  out=[]
  for name,score,box in raw[:config.MAX_DETECTIONS]:
   x1,y1,x2,y2=box; d=self.distance.calculate(name,box)
   out.append(Detection(name,score,box,((x1+x2)/2,(y1+y2)/2),get_direction(box,w),d,self.distance.classify(d)))
  return out
 def _detect_onnx(self,frame):
  h,w=frame.shape[:2]; s=config.INFERENCE_SIZE
  blob=cv2.dnn.blobFromImage(cv2.resize(frame,(s,s)),1/255,(s,s),swapRB=True,crop=False)
  self.net.setInput(blob); pred=np.asarray(self.net.forward())
  if pred.ndim==3:pred=pred[0]
  if pred.ndim!=2:return []
  if pred.shape[0] in (84,85) and pred.shape[0]<pred.shape[1]:pred=pred.T
  boxes=[];scores=[];classes=[]
  for row in pred:
   if len(row)<5:continue
   cid=int(np.argmax(row[4:])); score=float(row[4+cid])
   if score<config.CONFIDENCE_THRESHOLD or cid>=len(COCO_NAMES):continue
   cx,cy,bw,bh=map(float,row[:4]); x1=max(0,int((cx-bw/2)*w/s)); y1=max(0,int((cy-bh/2)*h/s)); x2=min(w-1,int((cx+bw/2)*w/s)); y2=min(h-1,int((cy+bh/2)*h/s))
   if x2<=x1 or y2<=y1:continue
   boxes.append([x1,y1,x2-x1,y2-y1]);scores.append(score);classes.append(cid)
  idx=cv2.dnn.NMSBoxes(boxes,scores,config.CONFIDENCE_THRESHOLD,config.NMS_THRESHOLD); out=[]
  for i in (np.asarray(idx).reshape(-1)[:config.MAX_DETECTIONS] if len(idx) else []):
   x,y,bw,bh=boxes[int(i)];out.append((COCO_NAMES[classes[int(i)]],scores[int(i)],(float(x),float(y),float(x+bw),float(y+bh))))
  return out
