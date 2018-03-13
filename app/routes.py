from app import app, db
from flask import jsonify, request
from data.data import Event, Point, PointProp, EventProp
from json import dumps as jdumps
from geojson import loads as gloads
from shapely.geometry import shape

hello_world_data = {'data' : 'HELLO WORLD!'}
string_list = ["hello", "world", "plzzzz"]

# Is this strictly necessary?
@app.route('/api/events/<event_id>/points', methods=['GET'])
def get_points(event_id):
    return None


@app.route('/api/events', methods=['POST'])
def set_event():
    return None

@app.route('/api/events/nearby', methods=['GET'])
def get_nearby_events():
    # For now this just returns all of the mock events
    return md.get_events()

@app.route('/api/events/<event_id>', methods=['GET'])
def get_event_by_id(event_id):
    # For now this returns one event with the given id
    # The event is the same for all ids
    return md.get_event(event_id=event_id)

@app.route('/api/events/<event_id>', methods=['POST'])
def update_event(event_id):
    return None

@app.route('/api/events/<event_id>/points', methods=['POST'])
def set_points(event_id):
    return None



# The following routes are test endpoints!!!
@app.route('/api/test/point/<pid>')
def send_test_point(pid):
    return md.get_point(pid)

@app.route('/api/test/event/<eid>')
def send_test_event(eid):
    return md.get_event(eid)

@app.route('/api/test/events')
def send_test_events():
    return md.get_events()

@app.route('/api/test/point', methods=['POST'])
def recieve_test_point():
    json = request.get_json()
    # md.parse_point(json)
    return jsonify(json)

@app.route('/api/test/event', methods=['POST'])
def recieve_test_event():
    rjson = request.get_json()
    features = rjson['features']
    plist = []
    for f in features:
        geo = f['geometry']
        props = f['properties']
        proplist = []
        for key, value in props.items():
            proplist.append(PointProp(prop_name=key, prop=value))
        geo = jdumps(geo)
        geo = gloads(geo)
        point = shape(geo)
        wkt = 'SRID=4326;' + point.wkt
        plist.append(Point(point=wkt, props=proplist))
    e = Event(points=plist)
    db.session.add(e)
    db.session.flush()
    db.session.commit()
    
    # with open('test.json', 'w') as f:
    #     json.dump(rjson, f)
    return jsonify(rjson)

@app.route('/')
def hello_world():
    return jsonify(string_list)
