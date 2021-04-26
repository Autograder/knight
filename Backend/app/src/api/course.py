
from flask_cors import CORS
from flask import Blueprint, request, jsonify
from flask_login import current_user
from ..security.roles import role_required, URole
from ..models.course import Course, Quarter
from ..models.queue import Queue, Status
from ..models.user import User
from ..utils.time import TimeUtil

course_api_bp = Blueprint('course_api', __name__)
CORS(course_api_bp, supports_credentials=True)


@course_api_bp.route('/create_course', methods=['POST'])
# @role_required(role=URole.ADMIN.value)
def create_course():
    """
    @author : @mihaivaduva21
    @updates: YixuanZ
    Creates a course, only users with ADMIN role should call this.
    """
    u = User.get_user_by_id(user_id=current_user.id)
    if not u.is_instructor():
        return jsonify({'reason': 'only instructors can create course'}), 400
    req = request.get_json()
    description = req.get('description', '')
    name = req.get('name', '')
    quarter = Quarter[str(req.get('quarter'))].value
    short_name = req.get('short_name', '')
    url = req.get('url', None)
    year = int(req.get('year', TimeUtil.get_current_year()))
    active = bool(req.get('active', True))
    queue_enabled = bool(req.get('queue_enabled', True))
    cse = bool(req.get('cse', True))
    queue_lock = bool(req.get('queue_lock', False))

    hce = True
    hct = 25
    hcm = None
    hcw = None
    tc = 10

    queue = Queue.create_queue(status=Status.CLOSED,
                               high_capacity_enable=hce,
                               high_capacity_threshold=hct,
                               high_capacity_message=hcm,
                               high_capacity_warning=hcw,
                               ticket_cool_down=tc,
                               queue_lock=queue_lock)

    queue_id = queue.id

    crs = Course.create_course(description=description, name=name,
                               quarter=quarter, short_name=short_name, url=url,
                               year=year, active=active,
                               queue_enabled=queue_enabled, cse=cse,
                               queue_id=queue_id,
                               instructor_id=current_user.id)
    if crs is not None:
        return jsonify({'reason': 'course created',
                        'result': crs.to_json()}), 200
    else:
        return jsonify({'reason': 'course existed'}), 300


@course_api_bp.route('/delete_course', methods=['POST'])
# @role_required(role=URole.ADMIN.value)
def delete_course():
    """
    @author : @mihaivaduva21
    """
    quarter = Quarter[str(request.json['quarter'])].value
    short_name = str(request.json['short_name'])
    year = int(request.json['year'])

    if Course.delete_course(quarter=quarter, short_name=short_name,
                            year=year) is True:
        return jsonify({'reason': 'course deleted'}), 200
    else:
        return jsonify({'reason': 'course non-existent'}), 300


@course_api_bp.route('/find_course_by_id', methods=['GET'])
def find_course_by_id():
    """
    @author: @sccontre
    """
    id = request.args.get('id', type=int)
    c = Course.get_course_by_id(id)
    if c is None:
        return jsonify({'reason': 'course not found'}), 400
    else:
        return jsonify({'reason': 'course found', 'result': c.to_json()}), 200


@course_api_bp.route('/find_all_courses', methods=['GET'])
def find_all_courses():
    """
    @author: YixuanZ
    """
    try:
        q = Quarter[request.args.get('quarter', type=str)].value
    except KeyError:
        q = None
    y = request.args.get('year', type=int)
    crs = Course.get_all_courses(quarter=q, year=y)
    crs = list(map(lambda x: x.to_json(), crs))
    return jsonify({'reason': 'successed', 'result': crs}), 200