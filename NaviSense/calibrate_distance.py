"""Calibrate focal length from a known object at a measured distance."""
import argparse,cv2,config
from distance_calculator import DistanceCalculator,KNOWN_OBJECT_HEIGHTS
def main():
 p=argparse.ArgumentParser();p.add_argument('--object',default='person',choices=sorted(KNOWN_OBJECT_HEIGHTS));p.add_argument('--distance',type=float,required=True);p.add_argument('--camera',type=int,default=config.CAMERA_INDEX);a=p.parse_args()
 if a.distance<=0:raise ValueError('--distance must be positive')
 from ultralytics import YOLO
 model=YOLO(str(config.MODEL_PT));cap=cv2.VideoCapture(a.camera)
 if not cap.isOpened():raise RuntimeError(f'Cannot open camera index {a.camera}')
 print('Keep the full reference object visible. Press C to save calibration, Q to quit.')
 try:
  while True:
   ok,frame=cap.read()
   if not ok:raise RuntimeError('Camera stopped returning frames')
   r=model.predict(frame,imgsz=config.INFERENCE_SIZE,conf=config.CONFIDENCE_THRESHOLD,verbose=False,device='cpu')[0];box=None
   for b in r.boxes:
    if r.names[int(b.cls[0])]==a.object:box=tuple(map(float,b.xyxy[0].tolist()));break
   if box:
    x1,y1,x2,y2=map(int,box);cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
   cv2.putText(frame,f'{a.object} at measured {a.distance}m | C=save, Q=quit',(10,25),cv2.FONT_HERSHEY_SIMPLEX,.55,(255,255,255),2)
   cv2.imshow('NaviSense calibration',frame);k=cv2.waitKey(1)&255
   if k==ord('c') and box:
    focal=DistanceCalculator.focal_from_sample(a.distance,KNOWN_OBJECT_HEIGHTS[a.object],abs(box[3]-box[1]));DistanceCalculator().save_calibration(focal,frame.shape[1]);print(f'Saved focal length {focal:.2f}px for width {frame.shape[1]}');break
   if k in (ord('q'),27):break
 finally:cap.release();cv2.destroyAllWindows()
if __name__=='__main__':main()
