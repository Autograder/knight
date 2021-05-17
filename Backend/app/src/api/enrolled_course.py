from flask_cors import CORS
# from flask_login import login_required, current_user
from flask_login import current_user
from flask import Blueprint, request, jsonify

from ..models.user import User
from ..models.enrolled_course import Role, EnrolledCourse

enrolled_course_api_bp = Blueprint('enrolled_course_api', __name__)
CORS(enrolled_course_api_bp)

# We should follow the GET -> args.get and POST -> json, need to test for CORS


def is_instructor_of_course(course_id: int) -> bool:
    """
    Check whether the current user is the instructor of a course.
    @author: YixuanZ
    """
    c_u_id = current_user.id
    ecu = EnrolledCourse.find_user_in_course(user_id=c_u_id,
                                             course_id=course_id)
    return ecu.get_role() <= Role.INSTRUCTOR.value


@enrolled_course_api_bp.route('/enroll_user', methods=['POST'])
# @login_required
def enroll_user():
    """
    Route to enroll a user in to a specific section of a course.
    When the role field of the request is empty, the default would be student.
    @authoer YixuanZ
    """
    req = request.get_json()
    user_id = int(req['user_id'])
    role = Role[req['role']].value if 'role' in req else Role['STUDENT'].value
    section_id = int(req['section_id'])
    course_id = int(req['course_id'])
    # Check the authroity of the operation
    """
    if not is_instructor_of_course(course_id)
        return jsonify({'reason': 'Method is forbiden from you'}), 400
    """
    if EnrolledCourse.enroll_user_to(user_id=user_id,
                                     course_id=course_id,
                                     section_id=section_id,
                                     role=role):
        return jsonify({'reason': 'user enrolled'}), 200
    else:
        return jsonify({'reason': 'user existed'}), 300


@enrolled_course_api_bp.route('/change_role', methods=['POST'])
# @login_required
def change_role():
    """
    Change the role of the enrolled user in a course.
    """
    # Check the authroity of the operation
    """
    if not is_instructor_of_course(course_id)
        return jsonify({'reason': 'Method is forbiden from you'}), 400
    """
    req = request.get_json()
    uid = int(req['user_id'])
    cid = int(req['course_id'])
    role = Role[req['role']]
    ec = EnrolledCourse.find_user_in_course(user_id=uid, course_id=cid)
    if not ec:
        return jsonify({'reason': "User not enrolled"}), 400
    ec.change_role(role)
    return jsonify({'reason': 'Role changed'}), 200


@enrolled_course_api_bp.route('/delete_user_from_course', methods=['POST'])
# @login_required
def delete_user_from_course():
    """
    The route to remote an user from a particular course.
    """
    req = request.get_json()
    user_id = int(req['user_id'])
    course_id = int(req['course_id'])
    # Check the authroity of the operation
    """
    if not is_instructor_of_course(course_id):
        return jsonify({'reason': 'Method is forbiden from you'}), 400
    """
    if EnrolledCourse.delete_enrolled_user_from_course(user_id=user_id,
                                                       course_id=course_id):
        return jsonify({'reason': 'user deleted'}), 200
    else:
        return jsonify({'reason': 'user not found'}), 400


@enrolled_course_api_bp.route('/get_user_in_course', methods=['GET'])
# @login_required
def get_user_in_course():
    """
    Route to get a user from a specific course.
    """
    user_id = request.args.get('user_id', type=int)
    course_id = request.args.get('course_id', type=int)
    ec = EnrolledCourse.\
        find_user_in_course(user_id=user_id,
                            course_id=course_id)
    ec_info = ec.to_json() if ec is not None else {}
    user = User.get_user_by_id(user_id)
    user_info = user.to_json()
    ret = {'user_info': user_info, 'enrolled_course_info': ec_info}
    return jsonify({'reason': 'success', 'result': ret}), 200


@enrolled_course_api_bp.route('/get_all_user_in_course', methods=['GET'])
# @login_required
def get_all_user_in_course():
    """
    Route to get all the users of that is in a given course.\n
    The roles is optional, when passing in,
    pass in the string representation of ; seperated int values.
    """
    course_id = request.args.get('course_id')
    rs = request.args.get('roles', type=str)
    roles = None
    if rs:
        roles = []
        rs = rs.split(';')
        for r in rs:
            roles.append(Role[r].value)

    status, ec_list = EnrolledCourse.\
        find_all_user_in_course(course_id=course_id, role=roles)
    if status:
        ret = []
        i = 0
        for ec in ec_list:
            i += 1
            user = User.get_user_by_id(ec.user_id)
            scr = {}
            scr['user_info'] = user.to_json()
            scr['enrolled_user_info'] = ec.to_json()
            ret.append(scr)
        return jsonify({'reason': 'success', 'result': ret}), 200
    else:
        return jsonify({'reason': 'course not found'}), 400


@enrolled_course_api_bp.route('/get_user_in_section', methods=['GET'])
# @login_required
def get_user_in_section():
    """
    The route to remote an user from a particular course.
    """
    sid = request.args.get('section_id', type=int)
    cid = request.args.get('course_id', type=int)
    ecs = EnrolledCourse.find_all_user_in_section(course_id=cid,
                                                  section_id=sid)

    roles = request.args.get('roles', default=None, type=str)

    if roles:
        roles = set(roles.split(';'))

    ret = []

    for ec in ecs:
        if roles and Role(ec.role).name not in roles:
            continue

        user = User.get_user_by_id(ec.user_id)

        scr = {}
        scr['user_info'] = user.to_json()
        scr['enrolled_user_info'] = ec.to_json()
        ret.append(scr)

    return jsonify({'reason': 'success', 'result': ret}), 200


@enrolled_course_api_bp.route('/get_courses_user_in',
                              methods=['GET'])
# @login_required
def get_courses_user_in():
    """
    Route to get all the courses that a user is in.
    There can be a role being specified, if not,
    all the courses will be returned regardless of the role.
    """
    user_id = request.args.get('user_id', type=int)
    rs = request.args.get('roles', type=str)
    roles = None
    if rs:
        rs = rs.split(';')
        roles = []
        for r in rs:
            roles.append(Role[r].value)

    r = EnrolledCourse.find_courses_user_in(user_id=user_id,
                                            role=roles)
    i = 0
    ret = {}
    user = User.get_user_by_id(user_id)
    ret['user_info'] = user.to_json()
    courses = []
    for ec in r:
        i += 1
        scr = {}
        scr['enrolled_user_info'] = ec.to_json()
        courses.append(scr)
    ret['courses'] = courses
    return jsonify({'reason': 'success', 'result': ret}), 200


@enrolled_course_api_bp.route('/find_active_tutor_for', methods=['GET'])
# @login_required
def find_active_tutor_for():
    queue_id = int(request.args.get('queue_id', type=int))
    result = EnrolledCourse.find_active_tutor_for(queue_id=queue_id)
    users = result[2]
    ret = list(map(lambda user: user.to_json(), users))

    return jsonify({'reason': result[0], 'result': ret}), 200
