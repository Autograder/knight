from flask_cors import CORS
from flask import Blueprint, request, jsonify


from ..models.seating_layout import SeatingLayout


seating_layout_api_bp = Blueprint('seating_layout_api', __name__)
CORS(seating_layout_api_bp, supports_credentials=True)


@seating_layout_api_bp.route('/add', methods=['POST'])
def add():
    '''
    Route used to create a new seating layout in the DB. Only accepts
    POST requests.\n
    The `seats` field and the `count` field do not have to be present in the
    body of the POST request.
    @author james-c-lars
    '''
    location = request.json.get('location')
    seats = request.json.get('seats', None)
    count = request.json.get('count', None)

    status, layout = SeatingLayout.create_layout(location, seats, count)

    # If a layout at that location already existed
    if not status:
        return jsonify({'reason': 'location already exists'}), 300

    return jsonify({'reason': 'layout created'}), 200


@seating_layout_api_bp.route('/update', methods=['PUT'])
def update():
    '''
    Route used to update an existing seating layout in the DB. Only accepts
    PUT requests.\n
    The `seats` field and the `count` field do not have to be present in the
    body of the PUT request.
    @author james-c-lars
    '''
    location = request.json.get('location')
    seats = request.json.get('seats', None)
    count = request.json.get('count', None)

    layout = SeatingLayout.find_by_location(location)

    # If a layout at that location was not found
    if not layout:
        return jsonify({'reason': "layout doesn't exist"}), 300

    layout.seats = seats
    layout.count = count
    layout.save()

    return jsonify({'reason': 'layout updated'}), 200


@seating_layout_api_bp.route('/get', methods=['GET'])
def get():
    '''
    Route used to get a particular layout. Either location or layout_id can be
    provided. If both are given, location is prioritized in the search.
    @author james-c-lars
    '''
    layout_id = request.args.get('layout_id', None, type=int)
    location = request.args.get('location', None, type=str)

    layout = SeatingLayout.find_by_location(location)

    if not layout:
        layout = SeatingLayout.find_by_id(layout_id)

    # If a layout at that location was not found
    if not layout:
        return jsonify({'reason': "layout doesn't exist"}), 300

    return jsonify({'reason': 'request OK', 'result': layout.to_json()}), 200


@seating_layout_api_bp.route('/get_all', methods=['GET'])
def get_all():
    '''
    Route used to get all layouts stored in the database.
    @author james-c-lars
    '''
    layouts = [layout.to_json() for layout in SeatingLayout.get_all_layouts()]

    return jsonify({'reason': 'request OK', 'result': layouts}), 200
