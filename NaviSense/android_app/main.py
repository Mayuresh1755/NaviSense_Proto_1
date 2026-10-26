"""Kivy mobile UI; camera frames feed the shared ONNX/OpenCV detector."""
import sys,time
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty,BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera

KV = r'''
<NaviRoot>:
    orientation: 'vertical'
    padding: '8dp'
    spacing: '6dp'
    Label:
        text: 'NaviSense'
        size_hint_y: None
        height: '40dp'
        font_size: '23sp'
        bold: True
    Label:
        text: root.status
        size_hint_y: None
        height: '44dp'
        text_size: self.width, None
        halign: 'center'
        valign: 'middle'
    Camera:
        id: camera
        resolution: (640, 480)
        play: root.running
        allow_stretch: True
        keep_ratio: True
    Label:
        text: root.results
        text_size: self.width, None
        size_hint_y: None
        height: '100dp'
        halign: 'left'
        valign: 'top'
    BoxLayout:
        size_hint_y: None
        height: '48dp'
        spacing: '5dp'
        Button:
            text: 'Pause' if root.running else 'Start'
            on_release: root.toggle()
        Button:
            text: 'Explore'
            on_release: root.mode = 'explore'
        Button:
            text: 'Find target'
            on_release: root.mode = 'target'
    TextInput:
        id: target
        hint_text: 'Target label (e.g. bottle, person, backpack)'
        multiline: False
        size_hint_y: None
        height: '42dp'
        on_text: root.target_name = self.text
    Label:
        text: 'Approximate distances only. Not a certified mobility aid.'
        size_hint_y: None
        height: '32dp'
        font_size: '11sp'
'''
class NaviRoot(BoxLayout):
 status=StringProperty('Loading detector…');results=StringProperty('No detections yet.');running=BooleanProperty(False);mode=StringProperty('explore');target_name=StringProperty('')
 def __init__(self,**kwargs):
  super().__init__(**kwargs);self.detector=None;self.speech=None;self.event=None;self.last_infer=0
 def on_kv_post(self,*args):
  try:
   from detector import NaviDetector
   from speech import Speech
   self.detector=NaviDetector('onnx');self.speech=Speech(True);self.status='Model ready. Press Start.'
  except Exception as e:self.status=f'Model setup error: {type(e).__name__}: {e}'
 def toggle(self):
  self.running=not self.running
  if self.running and self.event is None:self.event=Clock.schedule_interval(self.process_frame,.2)
  elif not self.running and self.event is not None:self.event.cancel();self.event=None
  self.status='Running' if self.running else 'Paused'
 def process_frame(self,dt):
  if not self.running or self.detector is None:return
  texture=self.ids.camera.texture
  if texture is None:return
  if time.monotonic()-self.last_infer<.18:return
  self.last_infer=time.monotonic()
  try:
   import numpy as np,cv2
   pixels=np.frombuffer(texture.pixels,dtype=np.uint8)
   if pixels.size==texture.width*texture.height*4:
    frame=pixels.reshape(texture.height,texture.width,4)
    frame=cv2.cvtColor(frame,cv2.COLOR_RGBA2BGR)
   elif pixels.size==texture.width*texture.height*3:
    frame=pixels.reshape(texture.height,texture.width,3)
    frame=cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
   else:return
   frame=cv2.flip(frame,0)
   detections=self.detector.detect(frame)
   if self.mode=='target' and self.target_name.strip():detections=[d for d in detections if self.target_name.strip().lower() in d.name.lower()]
   detections.sort(key=lambda d:(d.distance is None,d.distance if d.distance else 1e6))
   lines=[f'{d.name}: {d.distance:.1f} m, {d.direction} ({d.category})' if d.distance else f'{d.name}: distance unknown, {d.direction}' for d in detections[:5]]
   self.results='\n'.join(lines) if lines else 'No matching objects detected.'
   urgent=[d for d in detections if d.distance and d.distance<=1.5]
   if urgent and self.speech:
    d=min(urgent,key=lambda x:x.distance);self.speech.say(f'{d.name}, {d.distance:.1f} metres, {d.direction}',key=f'{d.name}:{d.direction}:{d.category}',interval=2.5)
   self.status=f'{len(detections)} detected | {self.mode.title()} mode'
  except Exception as e:self.status=f'Frame processing error: {type(e).__name__}: {e}'
class NaviSenseApp(App):
 def build(self):self.title='NaviSense';Builder.load_string(KV);return NaviRoot()
 def on_stop(self):
  if self.root and self.root.event:self.root.event.cancel()
if __name__=='__main__':NaviSenseApp().run()
