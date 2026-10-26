import math
from distance_calculator import DistanceCalculator
def test_focal_from_sample():assert math.isclose(DistanceCalculator.focal_from_sample(2,1,100),200)
def test_manual_distance():
 d=DistanceCalculator(calibration_file='/nonexistent/calibration.json');d.configure_camera(640,480);d.focal_length=500
 assert math.isclose(d.calculate('person',(100,100,200,270)),5)
def test_unknown_object_returns_none():
 d=DistanceCalculator(calibration_file='/nonexistent/calibration.json');d.configure_camera(640,480)
 assert d.calculate('cell phone',(10,10,90,90)) is None
def test_invalid_calibration_rejected():
 try:DistanceCalculator.focal_from_sample(0,1,10)
 except ValueError:return
 assert False,'Expected ValueError'
