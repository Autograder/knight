from flask_cors import CORS
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from ..models.queue import Queue, Status, ActionType
from ..models.enrolled_course import EnrolledCourse, Role
from ..models.course import Course
from ..models.ticket import Status as t_Status
from ..models.queue_calendar import QueueCalendar


queue_api_bp = Blueprint('queue_api', __name__)
CORS(queue_api_bp, supports_credentials=True)


def user_in_course(queue_id: int, course_id: int) -> bool:
    """
    Checking whether the user is enrolled in the course.
    """
    course = Course.get_course_by_queue_id(queue_id)
    c_u_id = current_user.id
    if EnrolledCourse.find_user_in_course(user_id=c_u_id,
                                          course_id=course.id):
        return True
    else:
        return False


def user_own_queue(queue_id: int) -> bool:
    """
    Checking whetehr the user is the instructor of the course
    that has this queue.
    """
    course = Course.get_course_by_queue_id(queue_id)
    c_u_id = current_user.id
    ec_entry = EnrolledCourse.find_user_in_course(user_id=c_u_id,
                                                  course_id=course.id)
    if ec_entry:
        if ec_entry.role == Role.INSTRUCTOR.value:
            return True
    return False


@queue_api_bp.route('/find_queue', methods=['GET'])
#@login_required
def find_queue():
    """
    Return the queue object corresponding to an id.\n
    @authoer: YixuanZhou
    """
    queue_id = request.args.get('queue_id', type=int)
    if not queue_id:
        return jsonify({'reason': 'queue_id invalid'}), 400

    if not user_in_course:
        return jsonify({'reason': 'user not enrolled'}), 400

    queue = Queue.get_queue_by_id(queue_id)

    if not queue:
        return jsonify({'reason': 'queue not found'}), 400

    ret = {'reason': 'success', 'result': queue.to_json()}
    return jsonify(ret), 200


@queue_api_bp.route('/create_queue', methods=['POST'])
#@login_required
# @role_required(role=URole.ADMIN.value)
def create_queue():
    """
    Create a queue for a course.\n
    """
    req = request.get_json()
    hce = bool(req.get('high_capacity_enabled', None))
    hct = int(req.get('high_capacity_threshold', None))
    hcm = req.get('high_capacity_message', None)
    tc = int(req.get('ticket_cooldown', None))
    hcw = req.get('high_capacity_warning', None)
    q = Queue(status=Status.CLOSED.value,
              high_capacity_enable=hce,
              high_capacity_threshold=hct,
              high_capacity_message=hcm,
              high_capacity_warning=hcw,
              ticket_cool_down=tc,
              queue_lock=True
              )
    Queue.add_to_db(q)
    return jsonify({'reason': 'queue created'}), 200


@queue_api_bp.route('/update_queue_setting', methods=['POST'])
# @login_required
def update_queue_setting():
    req = request.get_json()
    q_id = req.get('queue_id', 0)
    if not user_own_queue(q_id):
        return jsonify({'reason': 'user not own queue'}), 300
    hce = bool(req.get('high_capacity_enabled', False))
    hct = int(req.get('high_capacity_threshold', 25))
    hcm = req.get('high_capacity_message', None)
    tc = int(req.get('ticket_cooldown', 10))
    hcw = req.get('high_capacity_warning', None)
    q = Queue.update_queue_setting(queue_id=q_id,
                                   high_capacity_enable=hce,
                                   high_capacity_threshold=hct,
                                   high_capacity_message=hcm,
                                   high_capacity_warning=hcw,
                                   ticket_cool_down=tc,
                                   queue_lock=True
                                   )
    return jsonify({'reason': 'success', 'result': q.to_json()}), 200


@queue_api_bp.route('/login_grader', methods=['POST'])
#@login_required
def login_grader():
    """
    Login a certain grader.
    """
    q_id = int(request.json['queue_id'])
    g_id = int(request.json['user_id'])  # g_id = current_user.id
    a_c = ActionType[request.json['action_type']].value  # need to change to string (name of the enum)
    result = Queue.grader_login(queue_id=q_id,
                                grader_id=g_id,
                                action_type=a_c)
    if result[0]:
        return jsonify({'reason': 'grader login'}), 200
    else:
        return jsonify({'reason': result[1]}), 400


@queue_api_bp.route('/logout_grader', methods=['POST'])
#@login_required
def logout_grader():
    """
    Logout a certain grader
    """
    q_id = request.json['queue_id']
    g_id = request.json['user_id']
    a_c = ActionType[request.json['action_type']].value
    status, result = Queue.grader_logout(queue_id=q_id,
                                         grader_id=g_id,
                                         action_type=a_c)
    if status:
        return jsonify({'reason': 'grader logout'}), 200
    else:
        return jsonify({'reason': result}), 400


@queue_api_bp.route('/find_queue_for_user', methods=['GET'])
#@login_required
def find_queue_for_user():
    """
    Find all the queues that this user is in.
    """
    uid = request.args.get('user_id', type=int)
    status, mess, q_list = Queue.\
        find_current_queue_for_user(user_id=uid)
    if status:
        return jsonify({'reason': 'success', 'result': q_list}), 200
    else:
        return jsonify({'reason': mess}), 400


@queue_api_bp.route('/lock_queue', methods=['POST'])
#@login_required
def lock_queue():
    """
    Lock the queue.
    """
    qid = request.json['queue_id']
    q = Queue.get_queue_by_id(queue_id=qid)
    if not q:
        return jsonify({'reason': 'queue not found'}), 400
    else:
        q.lock()
        return jsonify({'reason': 'success'}), 200


@queue_api_bp.route('/find_queue_for_course', methods=['GET'])
#@login_required
def find_queue_for_course():
    """
    Find the queue for a given course.
    """
    c_id = request.args.get('course_id', type=int)
    sta, q = Queue.find_queue_for_course(course_id=c_id)
    if sta:
        return jsonify({'reason': 'success', 'result': q.to_json()}), 200
    else:
        return jsonify({'reason': 'queue not found'}), 400


@queue_api_bp.route('/create_queue_calendar', methods=['POST'])
#@login_required
def create_queue_calendar():
    """
    Create the queue_calendar for the queue.
    """
    url = request.json['url']
    color = request.json['color']
    enable = request.json['is_enabled']
    q_id = request.json['queue_id']

    QueueCalendar(url=url, color=color, is_enabled=enable, queue_id=q_id)
    return jsonify({'reason': 'success'}), 200


@queue_api_bp.route('/get_feedback_for_grader', methods=['GET'])
#@login_required
def get_feedback_for_grader():
    """
    Get feedback for grader in the queue.
    """
    q_id = request.args.get('queue_id')
    g_id = request.args.get('grader_id')

    feedbacks = Queue.get_feedback_for_grader(queue_id=q_id, grader_id=g_id)

    return jsonify({'reason': 'success', 'result': feedbacks}), 200
