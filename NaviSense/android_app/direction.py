import config
def get_direction(bbox,frame_width):
 if frame_width<=0 or bbox is None or len(bbox)!=4: return 'ahead'
 ratio=((float(bbox[0])+float(bbox[2]))/2)/float(frame_width)
 if ratio<config.LEFT_BOUNDARY:return 'left'
 if ratio>config.RIGHT_BOUNDARY:return 'right'
 return 'ahead'
