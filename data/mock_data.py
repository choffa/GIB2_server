import geojson
from geojson import Point, Feature
from .data import Event


def get_event(event_id=100):
    points = [Point((63.420334, 10.402592)), Point((63.418370, 10.406905)), Point((63.409948, 10.409640))]
    features = [Feature(geometry=g) for g in points]
    event_id = event_id
    dist = 342.1
    avg_time = '01:03:12'

    e = Event(event_id, *features, dist=dist, avg_time=avg_time)
    dump = geojson.dumps(e)
    return dump

def get_events():
    events = []
    for i in range(0,5):
        points = [Point((63.420334+i, 10.402592+i)), Point((63.418370+i, 10.406905+i)), Point((63.409948+i, 10.409640+i))]
        features = [Feature(geometry=g) for g in points]
        event_id = i+100
        dist = 342.1 + i*2.5
        avg_time = str(i) + ':03:12'
        
        e = Event(event_id, *features, dist=dist, avg_time=avg_time)
        events.append(e)
    
    dump = ','.join(geojson.dumps(e) for e in events)
    return '[' + dump + ']'

def test():
    points = [Point((63.420334, 10.402592)), Point((63.418370, 10.406905)), Point((63.409948, 10.409640))]
    return geojson.dumps(points)

def get_point(pid):
    f = Feature(pid, Point((63.420334, 10.402592)))
    return geojson.dumps(f)


def add_event(request):
    pass 




