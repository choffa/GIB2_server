from app import app, db
from flask import jsonify, request, abort
from data.data import Event, Point, PointProp, EventProp
from json import dumps as jdumps
from geojson import loads as gloads, dumps as gdumps
from shapely.geometry import shape
from sqlalchemy.exc import IntegrityError

hello_world_data = {'data' : 'HELLO WORLD!'}
string_list = ["hello", "world", "plzzzz"]

@app.route('/api/events', methods=['POST'])
def set_event():
    rjson = request.get_json()
    features = rjson['features']
    plist = []
    for f in features:
        geo = f['geometry']
        if geo['id'] > 0:
            plist.append(Point.query.filter(Point.pid == geo['id']).first())
        else:
            props = f['properties']
            proplist = []
            for key, value in props.items():
                proplist.append(PointProp(prop_name=key, prop=value))
            geo = jdumps(geo)
            geo = gloads(geo)
            point = shape(geo)
            wkt = 'SRID=4326;' + point.wkt
            plist.append(Point(point=wkt, props=proplist))
    
    props = rjson['properties']
    proplist = []
    for key, value in props.items():
        proplist.append(EventProp(prop_name=key, prop=value))

    e = Event(points=plist, props=proplist)
    db.session.add(e)
    db.session.flush()
    db.session.commit()
    
    return gdumps(e)

@app.route('/api/events/nearby', methods=['GET'])
def get_nearby_events():
    # print(request.args)
    events = Event.query.all()
    d = ','.join(gdumps(e) for e in events)
    d = '['+d+']'
    return d

@app.route('/api/events/<event_id>', methods=['GET'])
def get_event_by_id(event_id):
    e = Event.query.filter(Event.eid == event_id).first()
    return gdumps(e)

@app.route('/api/events/<event_id>/properties', methods=['PUT'])
def update_event(event_id):
    r = request.geo_json()
    eid = r['id']
    event = Event.query.filter(Event.eid == eid).first()
    if event not None:
        EventProp.query.filter(EventProp.eid == eid).delete()
        proplist = []
        for key, value in r.items():
            prop = EventProp(prop_name=key, prop=value)
            proplist.append(prop)
        event.props = plist
    db.session.flush()
    db.session.commit()
    else:
        abort(400)



@app.route('/api/events/<event_id>/points', methods=['POST'])
def set_points(event_id):
    r = request.get_json()
    for feature in r:
        geom = feature['geometry']
        coords = geom['coordinates']
        ewkt = 'SRID=4326;Point(' + str(coords[0]) + ' ' + str(coords[1]) + ')' 
        props = []
        for key, value in feature['properties'].items():
            props.append(PointProp(prop_name=key, prop=value))
        p = Point(point=ewkt, eid=event_id, props=props)
        try:
            db.session.add(p)
            db.session.flush()
        except IntegrityError:
            abort(400)
    db.session.commit()
    return ''


# The following routes are test endpoints!!!
# @app.route('/api/test/point/<pid>')
# def send_test_point(pid):
#     return md.get_point(pid)

# @app.route('/api/test/event/<eid>')
# def send_test_event(eid):
#     return md.get_event(eid)

# @app.route('/api/test/events')
# def send_test_events():
#     return md.get_events()

# @app.route('/api/test/point', methods=['POST'])
# def recieve_test_point():
#     json = request.get_json()
#     # md.parse_point(json)
#     return jsonify(json)

# @app.route('/api/test/event', methods=['POST'])
# def recieve_test_event():
#     rjson = request.get_json()
#     features = rjson['features']
#     plist = []
#     for f in features:
#         geo = f['geometry']
#         props = f['properties']
#         proplist = []
#         for key, value in props.items():
#             proplist.append(PointProp(prop_name=key, prop=value))
#         geo = jdumps(geo)
#         geo = gloads(geo)
#         point = shape(geo)
#         wkt = 'SRID=4326;' + point.wkt
#         plist.append(Point(point=wkt, props=proplist))
    
#     props = rjson['properties']
#     proplist = []
#     for key, value in props.items():
#         proplist.append(EventProp(prop_name=key, prop=value))

#     e = Event(points=plist, props=proplist)
#     db.session.add(e)
#     db.session.flush()
#     db.session.commit()
    
#     # with open('test.json', 'w') as f:
#     #     json.dump(rjson, f)
#     return jsonify(rjson)

# @app.route('/')
# def hello_world():
#     return jsonify(string_list)
