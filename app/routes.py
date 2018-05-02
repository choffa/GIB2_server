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

@app.route('/api/events', methods=['PUT', 'POST'])
@auth.login_required
def events():
    r = request.get_json()
    if request.method == 'POST':
        return set_event(r)
    elif request.method == 'PUT':
        return update_event(r)


def set_event(req):
    start_point, plist, proplist = extract_features(req)
    e = Event(start_point=start_point, points=plist, props=proplist)
    db.session.add(e)
    db.session.commit()
    print(e.start_point)
    for p in e.points:
        print(p)
    return gdumps(e)

def update_event(req):
    event_id = req['id']
    event = Event.query.filter(Event.eid == event_id).first()
    if event is None:
        abort(400)
    start_point, plist, proplist = extract_features(req['features'])
    e.start_point = start_point
    e.points = plist
    e.props = proplist
    db.session.commit()


def extract_features(req):
    features = req['features']
    plist = []
    start_point = None
    for f in features:
        if start_point is None:
            start_point = get_or_make_point(f)
        else:
            plist.append(get_or_make_point(f))
    props = req['properties']
    proplist = []
    for key, value in props.items():
        if key not in ['avg_time', 'avg_score', 'popularity']:
            proplist.append(EventProp(prop_name=key, prop=value))
    return start_point, plist, proplist

@app.route('/api/events/nearby', methods=['GET'])
def get_nearby_events():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    dist = request.args.get('dist')
    if not (lat and lng and dist):
        abort(400)
    user_point = WKTElement('POINT({} {})'.format(lng, lat))
    events = Event.query.join(Point, Event.start_point).filter(ST_Distance(Point.point, user_point) <= dist).all()
    return '[' + ','.join(gdumps(e) for e in events) + ']'

@app.route('/api/points/nearby', methods=['GET'])
@auth.login_required
def get_nearby_points():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    dist = request.args.get('dist')
    if not (lat and lng and dist):
        abort(400)
    user_point = WKTElement('POINT({} {})'.format(lng, lat))
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

@app.route('/api/user', methods=['POST'])
def user():
    r = request.get_json()
    username = r['username'].lower()
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


@app.route('/api/user/events', methods=['GET'])
@auth.login_required
def get_my_events():
    user = User.query.filter(User.username == auth.username().lower()).first()
    return '[' + ','.join(gdumps(e) for e in user.saved_events) + ']'

@app.route('/api/user/events/<event_id>', methods=['POST', 'DELETE'])
@auth.login_required
def add_or_remove_my_event(event_id):
    if request.method == 'POST':
        return add_my_event(event_id)
    elif request.method == 'DELETE':
        return remove_my_event(event_id)

@app.route('/api/events/<event_id>/finish', methods=['POST'])
def finish_event(event_id):
    uid = User.query.filter(User.username == auth.username().lower()).with_entities(User.uid).scalar()
    time = request.args.get('time') or '00:00:00'
    print(time)
    score = request.args.get('score')
    h, m, s = time.split(':')
    event_stat = EventStat(uid, event_id, hours=h, minutes=m, seconds=s, score=score)
    print(event_stat)
    db.session.add(event_stat)
    db.session.commit()
    e = Event.query.get(event_id)
    return gdumps(e)

def add_my_event(eid):
    user = User.query.filter(User.username == auth.username().lower()).first()
    e = Event.query.get(eid)
    user.saved_events.append(e)
    db.session.commit()
    return '[' + ','.join(gdumps(e) for e in user.saved_events) + ']'

def remove_my_event(eid):
    user = User.query.filter(User.username == auth.username().lower()).first()
    e = Event.query.get(eid)
    user.saved_events.remove(e)
    db.session.commit()
    return '[' + ','.join(gdumps(e) for e in user.saved_events) + ']'

@app.route('/')
def hello_world():
    print(request.args.get('test'))
    return jsonify(string_list)

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter(User.username == username.lower()).first()
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