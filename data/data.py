from app import db
from geoalchemy2.types import Geography
from geojson import Feature
from shapely.wkb import loads
from werkzeug.security import generate_password_hash as gph, check_password_hash as cph
from sqlalchemy.sql import func

event_point = db.Table('event_point', db.metadata, db.Column('eid', db.Integer, db.ForeignKey('events.eid')),
    db.Column('pid', db.Integer, db.ForeignKey('points.pid'))
)

my_events = db.Table('my_events', db.metadata, db.Column(('uid'), db.Integer, db.ForeignKey('users.uid')), 
    db.Column('eid', db.Integer, db.ForeignKey('events.eid'))
)


class Event(db.Model):
    __tablename__ = 'events'
    eid = db.Column(db.Integer, primary_key=True)
    start_point_id = db.Column(db.Integer, db.ForeignKey('points.pid'), nullable=False)
    start_point = db.relationship('Point')
    points = db.relationship('Point', secondary=event_point)
    props = db.relationship('EventProp')

    def __repr__(self):
        ps = []
        for p in self.points:
            ps.append(loads(bytes(p.point.data)).wkt)

        return 'id: {}\npoints: {}\nproperties: {}'.format(self.eid, ps, self.props)

    @property
    def __geo_interface__(self):
        features = []
        g = loads(bytes(self.start_point.point.data))
        props = {}
        for prop in self.start_point.props:
            props[prop.prop_name] = prop.prop
        f = Feature(id=self.start_point.pid, geometry=g, properties=props)
        features.append(f)
        for p in self.points:
            g = loads(bytes(p.point.data))
            props = {}
            for prop in p.props:
                props[prop.prop_name] = prop.prop
            f = Feature(id=p.pid, geometry=g, properties=props)
            features.append(f)
        props = {}
        for prop in self.props:
            props[prop.prop_name] = prop.prop
        props['avg_time'] = EventStat.calc_average_time(self.eid)
        props['avg_score'] = EventStat.calc_average_score(self.eid)
        props['popularity'] = EventStat.query.filter(EventStat.eid == self.eid).count()
        return {'type': 'FeatureCollection', 'id': self.eid, 'features': features, 'properties': props}
        
        
class Point(db.Model):
    __tablename__ = 'points'
    pid = db.Column(db.Integer, primary_key=True)
    props = db.relationship('PointProp')
    point = db.Column(Geography(geometry_type='POINT'))

    def __repr__(self):
        return '{}-{}'.format(self.pid, loads(bytes(self.point.data)).wkt)

    @property
    def __geo_interface__(self):
        g = loads(bytes(self.point.data))
        propdict = {}
        for prop in self.props:
            propdict[prop.prop_name] = prop.prop
        f = Feature(id=self.pid, geometry=g, properties=propdict)
        return f

class PointProp(db.Model):
    __tablename__ = 'point_properties'
    prid = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('points.pid'))
    prop_name = db.Column(db.String)
    prop = db.Column(db.String)
            
    def __repr__(self):
        return '{}-{}-{}-{}'.format(self.prid, self.pid, self.prop_name, self.prop)

class EventProp(db.Model):
    __tablename__ = 'event_properties'
    prid = db.Column(db.Integer, primary_key=True)
    eid = db.Column(db.Integer, db.ForeignKey('events.eid'))
    prop_name = db.Column(db.String)
    prop = db.Column(db.String)
            
    def __repr__(self):
        return '{}-{}-{}-{}'.format(self.prid, self.eid, self.prop_name, self.prop)

class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, index=True)
    pw_hash = db.Column(db.String)
    saved_events = db.relationship('Event', secondary='my_events')

    def __init__(self, username, password):
        self.username = username.lower()
        self.pw_hash = gph(password)
    
    def check_password(self, candidate):
        return cph(self.pw_hash, candidate)

class EventStat(db.Model):
    __tablename__ = 'event_stats'
    sid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'), index=True)
    eid = db.Column(db.Integer, db.ForeignKey('events.eid'), index=True)
    seconds_used = db.Column(db.Integer)
    score = db.Column(db.Integer)

    def __init__(self, uid, eid, hours=0, minutes=0, seconds=0, score=0):
        self.uid = uid
        self.eid = eid
        self.seconds_used = hours * 3600 + minutes * 60 + seconds
        self.score = score
    
    @staticmethod
    def calc_average_time(event_id):
        try:
            seconds = round(db.session.query(func.avg(EventStat.seconds_used)).filter(EventStat.eid == event_id).scalar())
        except TypeError:
            seconds = 0

        hours = seconds // 3600
        seconds = seconds % 3600
        minutes = seconds // 60
        seconds = seconds % 60

        return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
    
    @staticmethod
    def calc_average_score(event_id):
        try:
            avg_score = float(db.session.query(func.avg(EventStat.score)).filter(EventStat.eid == event_id).scalar)
        except TypeError:
            avg_score = 0
        return avg_score
    
    def __repr__(self):
        return 'sid: {}\nuid: {}\n eid: {}\nsecs: {}\nscore: {}'.format(self.sid, self.uid, self.eid, self.seconds_used, self.score)
