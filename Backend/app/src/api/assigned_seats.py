from flask_cors import CORS
from flask import Blueprint, request, jsonify


from ..models.assigned_seats import AssignedSeats


assigned_seats_api_bp = Blueprint('assigned_seats_api', __name__)
CORS(assigned_seats_api_bp, supports_credentials=True)


@assigned_seats_api_bp.route('/add', methods=['POST'])
def add():
    '''
    Route used to create a new seat assignment in the DB. Only accepts
    POST requests.\n
    The `seat_assignments` field does not have to be present in the
    body of the POST request.
    @author james-c-lars
    '''
    assignment_name = request.json.get('assignment_name')
    layout_id = request.json.get('layout_id')
    course_id = request.json.get('course_id')
    section_id = request.json.get('section_id')
    seat_assignments = request.json.get('seat_assignments', None)

    status, assignment = AssignedSeats.create_assignment(assignment_name,
                                                         layout_id, course_id,
                                                         section_id,
                                                         seat_assignments)

    # If an assignment with that name already existed
    if not status:
        return jsonify({'reason': 'assignment already exists'}), 300

    return jsonify({'reason': 'assignment created'}), 200


@assigned_seats_api_bp.route('/update', methods=['PUT'])
def update():
    '''
    Route used to update an existing seat assignment in the DB. Only accepts
    PUT requests.\n
    The `seat_assignments` field does not have to be present in the
    body of the POST request.
    @author james-c-lars
    '''
    assignment_name = request.json.get('assignment_name')
    layout_id = request.json.get('layout_id')
    course_id = request.json.get('course_id')
    section_id = request.json.get('section_id')
    seat_assignments = request.json.get('seat_assignments', None)

    assignment = AssignedSeats.find_by_name(assignment_name)

    # If an assignment with that name was not found
    if not assignment:
        return jsonify({'reason': "assignment doesn't exist"}), 300

    assignment.layout_id = layout_id
    assignment.course_id = course_id
    assignment.section_id = section_id
    assignment.seat_assignments = seat_assignments
    assignment.save()

    return jsonify({'reason': 'assignment updated'}), 200


@assigned_seats_api_bp.route('/get', methods=['GET'])
def get():
    '''
    Route used to get a particular seat assignment. We search by the name
    given in the GET request.
    @author james-c-lars
    '''
    assignment_name = request.args.get('assignment_name', type=str)

    assignment = AssignedSeats.find_by_name(assignment_name)

    # If a seat assignment with that name was not found
    if not assignment:
        return jsonify({'reason': "assignment doesn't exist"}), 300

    return jsonify({'reason': 'request OK', 'result': assignment.to_json()}),\
        200


@assigned_seats_api_bp.route('/get_all', methods=['GET'])
def get_all():
    '''
    Route used to get all seat assignments stored in the database.
    @author james-c-lars
    '''
    assignments = [assignment.to_json() for assignment in
                   AssignedSeats.get_all_assignments()]

    return jsonify({'reason': 'request OK', 'result': assignments}), 200


@assigned_seats_api_bp.route('/get_all_in_course', methods=['GET'])
def get_all_in_course():
    '''
    Route used to get all seat assignments for a course.
    @author james-c-lars
    '''
    course_id = request.args.get('course_id', type=int)

    assignments = [assignment.to_json() for assignment in
                   AssignedSeats.get_assignments_by_course_id(course_id)]

    return jsonify({'reason': 'request OK', 'result': assignments}), 200


@assigned_seats_api_bp.route('/get_all_in_section', methods=['GET'])
def get_all_in_section():
    '''
    Route used to get all seat assignments for a section.
    @author james-c-lars
    '''
    section_id = request.args.get('section_id', type=int)

    assignments = [assignment.to_json() for assignment in
                   AssignedSeats.get_assignments_by_section_id(section_id)]

    return jsonify({'reason': 'request OK', 'result': assignments}), 200
