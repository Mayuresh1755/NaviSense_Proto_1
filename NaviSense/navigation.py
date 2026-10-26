import config
def alert_for(d):
 if d.distance is None or d.distance<=0:return None
 level='critical' if d.distance<=config.CRITICAL_DISTANCE else 'warning' if d.distance<=config.WARNING_DISTANCE else 'safe'
 return {'level':level,'message':f'{level}: {d.name} {d.distance:.1f} metres {d.direction}','distance':d.distance}
