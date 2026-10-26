"""Manual monocular distance estimation using a pinhole-camera model."""
import json, math
from pathlib import Path
import config
KNOWN_OBJECT_HEIGHTS={"person":1.70,"chair":0.90,"table":0.75,"bottle":0.25,"cup":0.12,"laptop":0.25,"backpack":0.45,"car":1.50,"bicycle":1.10,"motorcycle":1.20,"bus":3.0,"truck":3.0,"dog":0.50,"cat":0.30,"bench":0.50,"tv":0.60,"potted plant":0.50,"suitcase":0.60,"umbrella":0.90}
class DistanceCalculator:
 def __init__(self,horizontal_fov=config.CAMERA_HORIZONTAL_FOV,calibration_file=config.CALIBRATION_FILE):
  if not 0<float(horizontal_fov)<180: raise ValueError('FOV must be between 0 and 180 degrees')
  self.horizontal_fov=float(horizontal_fov); self.calibration_file=Path(calibration_file); self.frame_width=None; self.frame_height=None; self.focal_length=None
 def configure_camera(self,frame_width,frame_height):
  if int(frame_width)<=0 or int(frame_height)<=0: raise ValueError('Frame dimensions must be positive')
  self.frame_width=int(frame_width); self.frame_height=int(frame_height)
  self.focal_length=(self.frame_width/2)/math.tan(math.radians(self.horizontal_fov)/2)
  try:
   d=json.loads(self.calibration_file.read_text(encoding='utf-8'))
   f=float(d['focal_length'])
   if int(d['frame_width'])==self.frame_width and math.isfinite(f) and f>0: self.focal_length=f
  except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError): pass
  return self.focal_length
 @staticmethod
 def focal_from_sample(distance_m,real_height_m,pixel_height):
  vals=(distance_m,real_height_m,pixel_height)
  if any(not math.isfinite(float(v)) or float(v)<=0 for v in vals): raise ValueError('Calibration values must be positive finite numbers')
  return float(distance_m)*float(pixel_height)/float(real_height_m)
 def save_calibration(self,focal_length,frame_width=None):
  width=int(frame_width or self.frame_width or 0); focal=float(focal_length)
  if width<=0 or not math.isfinite(focal) or focal<=0: raise ValueError('Invalid calibration')
  self.calibration_file.write_text(json.dumps({'focal_length':focal,'frame_width':width,'method':'manual_pinhole_calibration'},indent=2),encoding='utf-8')
  if width==self.frame_width: self.focal_length=focal
 def calculate(self,object_name,bbox):
  if self.focal_length is None: raise RuntimeError('Call configure_camera(width, height) first')
  if bbox is None or len(bbox)!=4: return None
  name=str(object_name).strip().lower(); height=KNOWN_OBJECT_HEIGHTS.get(name)
  if height is None: return None
  x1,y1,x2,y2=map(float,bbox); ph=abs(y2-y1); pw=abs(x2-x1)
  if not all(map(math.isfinite,(x1,y1,x2,y2))) or ph<2 or pw<2: return None
  # Width fallback only for an edge-cropped person that fills almost all the image height.
  if name=='person' and ph>=.90*self.frame_height and (y1<=2 or y2>=self.frame_height-2): d=self.focal_length*.45/pw
  else: d=self.focal_length*height/ph
  return float(d) if math.isfinite(d) and d>0 else None
 @staticmethod
 def classify(distance):
  if distance is None or not math.isfinite(float(distance)) or float(distance)<=0: return 'unknown'
  if distance<=config.CRITICAL_DISTANCE: return 'critical'
  if distance<=config.WARNING_DISTANCE: return 'warning'
  if distance<=3: return 'near'
  if distance<=5: return 'medium'
  return 'far'
