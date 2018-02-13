from app import app
from flask import jsonify, request


hello_world_data = {'data' : 'HELLO WORLD!'}

mock_points = [
    {
        'id' : 0,
        'location' : {
            'lat' : 0.00000,
            'lon' : 0.00000
        },
        'top' :'lorem ipsum dolor sit amet'
    },
    {
        'id' : 1,
        'location' : {
            'lat' : 1.00000,
            'lon' : 1.00000
        },
        'top' :'lorem ipsum dolor sit amet'
    },
    {
        'id' : 2,
        'location' : {
            'lat' : 2.00000,
            'lon' : 2.00000
        },
        'top' :'lorem ipsum dolor sit amet'
    }
]

mock_event = {
    'id' : 0,
    'points' : mock_points,
    'start_id' : 0,
    'end_id' : 2,
    'dist' : 500,
    'avg_time' : 100
}

@app.route('/')
def hello_world():
    return jsonify(hello_world_data)

@app.route('/api/points/<id>', methods=['GET'])
def get_points(id):
    return jsonify(mock_points[int(id)])


@app.route('/api/events', methods=['POST'])
def set_event():
    return None

@app.route('/api/events/nearby', methods=['GET'])
def get_nearby_events():
    return None

@app.route('/api/events/<id>', methods=['GET'])
def get_event_by_id(id):
    return jsonify(mock_event)

@app.route('/api/events/<id>', methods=['POST'])
def update_event(id):
    return None

@app.route('/api/events/<id>/points', methods=['POST'])
def set_points(id):
    return None


# @app.route('/users/<id>')
# def user(id):
#     return '<h1>' + str(id) + '</h1>'

# @app.route('/test')
# def test():
#     a = {}
#     a['aa'] = request.args.get('aa')
#     a['bb'] = request.args.get('bb')
#     return jsonify(a)
