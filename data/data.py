

class Event():
    def __init__(self, event_id, *features, **props):
        self.id = event_id
        self.props = props
        self.features = [f for f in features]

    @property
    def __geo_interface__(self):
        return {'type': 'FeatureCollection', 'features': self.features, 'properties': self.props}

