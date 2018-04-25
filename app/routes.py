from app import app, db, auth
from flask import jsonify, request, abort
from data.data import *
from json import dumps as jdumps
from geojson import loads as gloads, dumps as gdumps
from shapely.geometry import shape
from sqlalchemy.exc import IntegrityError
from geoalchemy2.functions import ST_Distance
from geoalchemy2.types import Geography
from geoalchemy2.elements import WKTElement

hello_world_data = {'data' : 'HELLO WORLD!'}
string_list = ["hello", "world", "plzzzz"]

@app.route('/api/events', methods=['POST'])
@auth.login_required
def set_event():
    rjson = request.get_json()
    features = rjson['features']
    plist = []
    start_point = None
    for f in features:
        if start_point is None:
            start_point = get_or_make_point(f)
        else:
            plist.append(get_or_make_point(f))
    props = rjson['properties']
    proplist = []
    for key, value in props.items():
        proplist.append(EventProp(prop_name=key, prop=value))
    e = Event(points=plist, start_point=start_point, props=proplist)
    db.session.add(e)
    db.session.commit()
    return gdumps(e)

@app.route('/api/events/nearby', methods=['GET'])
@auth.login_required
def get_nearby_events():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    dist = request.args.get('dist')
    if not (lat and lng and dist):
        abort(400)
    user_point = WKTElement('POINT({} {})'.format(lat, lng))
    events = Event.query.filter(ST_Distance(Event.start_point.point, user_point) <= dist).all()
    return '[' + ','.join(gdumps(e) for e in events) + ']'

@app.route('/api/points/nearby', methods=['GET'])
@auth.login_required
def get_nearby_points():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    dist = request.args.get('dist')
    if not (lat and lng and dist):
        abort(400)
    user_point = WKTElement('POINT({} {})'.format(lat, lng))
    points = Point.query.filter(ST_Distance(Point.point, user_point) <= dist).all()
    return '[' + ','.join(gdumps(p) for p in points) + ']'

@app.route('/api/points', methods=['PUT', 'POST'])
@auth.login_required
def points():
    r = request.get_json()
    if request.method == 'POST':
        return set_points(r)
    elif request.method == 'PUT':
        return update_point(r)

def set_points(req):
    plist = []
    for point in req:
        geom = point['geometry']
        coords = geom['coordinates']
        ewkt = 'Point(' + str(coords[0]) + ' ' + str(coords[1]) + ')' 
        props = []
        for key, value in point['properties'].items():
            props.append(PointProp(prop_name=key, prop=value))
        p = Point(point=ewkt, props=props)
        plist.append(p)
        db.session.add(p)
    db.session.flush()
    db.session.commit()
    d = ','.join(gdumps(p) for p in plist)
    d = '[' + d + ']'
    return d

def update_point(req):
    point = Point.query.filter(Point.pid == req['id']).first()
    if point is None:
        abort(400)
    geom = req['geometry']
    coords = geom['coordinates']
    ewkt = 'Point(' + str(coords[0]) + ' ' + str(coords[1]) + ')'
    props = []
    for key, value in req['properties'].items():
        props.append(PointProp(prop_name=key, prop=value))
    for prop in point.props:
        db.session.delete(prop)
    point.point = ewkt
    point.props = props
    db.session.flush()
    db.session.commit()
    return gdumps(point)

@app.route('/api/events/<event_id>', methods=['GET'])
@auth.login_required
def get_event_by_id(event_id):
    e = Event.query.filter(Event.eid == event_id).first()
    return gdumps(e)

@app.route('/api/events/<event_id>/properties', methods=['PUT'])
@auth.login_required
def update_event(event_id):
    r = request.get_json()
    event = Event.query.filter(Event.eid == event_id).first()
    if event is not None:
        EventProp.query.filter(EventProp.eid == event_id).delete()
        proplist = []
        for key, value in r.items():
            prop = EventProp(prop_name=key, prop=value)
            proplist.append(prop)
        event.props = proplist
        db.session.flush()
        db.session.commit()
    else:
        abort(400)
    return gdumps(event)

@app.route('/api/events/<event_id>/points', methods=['POST'])
def set_points_to_event(event_id):
    #r = request.get_json()
    #for feature in r:
    #    geom = feature['geometry']
    #    coords = geom['coordinates']
    #    ewkt = 'Point(' + str(coords[0]) + ' ' + str(coords[1]) + ')' 
    #    props = []
    #    for key, value in feature['properties'].items():
    #        props.append(PointProp(prop_name=key, prop=value))
    #    p = Point(point=ewkt, eid=event_id, props=props)
    #    try:
    #        db.session.add(p)
    #        db.session.flush()
    #    except IntegrityError:
    #        db.session.close()
    #        abort(400)
    #db.session.commit()
    #return ''
    event = Event.query.filter(Event.eid == event_id).first()
    if event in None:
        abort(400)
    return ''

@app.route('/api/users', methods=['POST'])
def users():
    r = request.get_json()
    username = r['username']
    password = r['password']
    user = User(username, password)
    try:
        db.session.add(user)
        db.session.flush()
        db.session.commit()
    except IntegrityError:
        db.session.close()
        return 'false'
    return 'true'

@app.route('/api/login', methods=['POST'])
@auth.login_required
def login_user():
    return jsonify(True)

@app.route('/api/events/<event_id>/time/<time>', methods=['POST'])
@auth.login_required
def post_time(event_id, time):
    times = time.split(':')
    if len(times) != 3:
        abort(400)
    user_id = User.query.filter(User.username == auth.username()).first().uid
    t = Time(event_id, user_id, times[0], times[1], times[2])
    db.session.add(t)
    db.session.commit()
    return gdumps(Event.query.filter(Event.eid == event_id).first()) 

@app.route('/')
def hello_world():
    return jsonify(string_list)

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter(User.username == username).first()
    if not user or not user.check_password(password):
        return False
    return True

def get_or_make_point(feature):
    pid = feature['id']
    point = Point.query.filter(Point.pid == pid).first()
    if point is not None:
        return point
    geo = feature['geometry']
    props = feature['properties']
    proplist = []
    for key, value in props.items():
        proplist.append(PointProp(prop_name=key, prop=value))
    geo = jdumps(geo)
    geo = gloads(geo)
    point = shape(geo)
    return Point(point=point.wkt, props=proplist)