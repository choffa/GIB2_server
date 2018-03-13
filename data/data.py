from app import db
from geoalchemy2.types import Geometry
from geojson import Feature, Point
from shapely.wkb import loads

class Event(db.Model):
    __tablename__ = 'events'
    eid = db.Column(db.Integer, primary_key=True)
    points = db.relationship('Point')

    def __init__(self, event_id, *points, **props):
        self.eid = int(event_id)
        self.props = props
        self.points = [p for p in points]

    def __repr__(self):
        return '{}-{}'.format(self.eid, self.points)

    @property
    def __geo_interface__(self):
        features = []
        for p in self.points:
            g = loads(bytes(p.point.data))
            f = Feature(id=p.pid, geometry=g)
            features.append(f)
        return {'type': 'FeatureCollection', 'id': self.eid, 'features': features}
        
        
class Point(db.Model):
    __tablename__ = 'points'
    pid = db.Column(db.Integer, primary_key=True)
    eid = db.Column(db.Integer, db.ForeignKey('events.eid'))
    prop = db.relationship('Prop')
    point = db.Column(Geometry(geometry_type='POINT', srid=4326))

    @property
    def __geo_interface__(self):
        return {'type': 'Point', 'coordinates': self.point}

    def __repr__(self):
        return '{}-{}-{}'.format(self.pid, self.eid, self.point)

class Prop(db.Model):
    __tablename__ = 'properties'
    prid = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('points.pid'))
    prop_name = db.Column(db.String)
    prop = db.Column(db.String)

    @property
    def __geo_interface__(self):
        geo = {}
        for i in range(prop):
            geo[self.prop_name] = self.prop
        return geo
    
    def __repr__(self):
        return '{}-{}-{}-{}'.format(self.prid, self.pid, self.prop_name, self.prop)
