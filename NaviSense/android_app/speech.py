import sys,threading,time
class Speech:
 def __init__(self,enabled=True):
  self.enabled=enabled;self.last={};self.lock=threading.Lock();self.engine=None
  if enabled and sys.platform!='android':
   try:import pyttsx3;self.engine=pyttsx3.init();self.engine.setProperty('rate',170)
   except Exception:self.engine=None
 def say(self,text,key=None,interval=2.0):
  if not self.enabled or not text:return
  now=time.monotonic();key=key or text
  with self.lock:
   if now-self.last.get(key,0)<interval:return
   self.last[key]=now
  if sys.platform=='android':
   try:from plyer import tts;tts.speak(text)
   except Exception:pass
  elif self.engine:
   def run():
    try:self.engine.say(text);self.engine.runAndWait()
    except Exception:pass
   threading.Thread(target=run,daemon=True).start()
