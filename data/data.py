from app import db
from geoalchemy2.types import Geometry
from geojson import Feature, Point as GPoint, FeatureCollection, dump as gdump
from shapely.wkb import loads
from werkzeug.security import generate_password_hash as gph, check_password_hash as cph

association_table = db.Table('event_point', db.metadata, db.Column(('eid'),db.Integer, db.ForeignKey('events.eid')),
    db.Column('pid', db.Integer, db.ForeignKey('points.pid'))
)

class Event(db.Model):
    __tablename__ = 'events'
    eid = db.Column(db.Integer, primary_key=True)
    points = db.relationship('Point', secondary=association_table)
    props = db.relationship('EventProp')

    # def __init__(self, event_id, *points, **props):
    #     self.eid = int(event_id)
    #     self.props = props
    #     self.points = [p for p in points]

    def __repr__(self):
        ps = []
        for p in self.points:
            ps.append(loads(bytes(p.point.data)).wkt)

        return '{}-{}-{}'.format(self.eid, ps, self.props)

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
        props['avg_time'] = str(DeltaTime(seconds=Time.calc_average_time(self.eid)))
        return {'type': 'FeatureCollection', 'id': self.eid, 'features': features, 'properties': props}
        
        
class Point(db.Model):
    __tablename__ = 'points'
    pid = db.Column(db.Integer, primary_key=True)
    props = db.relationship('PointProp')
    point = db.Column(Geometry(geometry_type='POINT', srid=4326))

    def __repr__(self):
        return '{}-{}-{}'.format(self.pid, self.eid, self.point)

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
    username = db.Column(db.String)
    pw_hash = db.Column(db.String)

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = gph(password)
    
    def check_password(self, candidate):
        return cph(self.pw_hash, candidate)

class Time(db.Model):
    __tablename__ = 'time'
    did = db.Column(db.Integer, primary_key=True)
    eid = db.Column(db.Integer, db.ForeignKey('events.eid'), index=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    seconds = db.Column(db.Integer)

    def __init__(self, eid, uid, hours=0, minutes=0, seconds=0):
        self.eid = eid
        self.uid = uid
        self.seconds = hours*3600 + minutes*60 + seconds

    @staticmethod
    def calc_average_time(event_id):
        seconds = [f.seconds for f in Time.query.filter(Time.eid == event_id).all()]
        if not len(seconds):
            return 0
        return round(sum(seconds)/len(seconds))

class DeltaTime():
    
    def __init__(self, hours=0, minutes=0, seconds=0):
        hours += seconds // 3600
        seconds = seconds % 3600
        minutes += seconds // 60
        seconds = seconds % 60

        hours += minutes // 60
        minutes = minutes % 60

        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
    
    def __repr__(self):
        return '{:02d}:{:02d}:{:02d}'.format(self.hours, self.minutes, self.seconds)
