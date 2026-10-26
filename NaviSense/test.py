
import time
from speech import Speech

speech = Speech()
speech.say("NaviSense audio test.", key="test", interval=0)
speech.say("Person ahead, approximately one metre.", key="person", interval=0)

time.sleep(5)
speech.close()
print("Speech test finished.")
