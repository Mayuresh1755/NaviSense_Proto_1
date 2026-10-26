from direction import get_direction
def test_left_center_right():
 assert get_direction((0,0,100,100),640)=='left'
 assert get_direction((250,0,390,100),640)=='ahead'
 assert get_direction((500,0,620,100),640)=='right'
def test_invalid_width():assert get_direction((0,0,1,1),0)=='ahead'
