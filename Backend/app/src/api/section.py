from flask_cors import CORS
from flask import Blueprint, request, jsonify
from flask_login import login_required

from ..models.section import Section

section_api_bp = Blueprint('section_api', __name__)
CORS(section_api_bp, supports_credentials=True)


@section_api_bp.route('/create_section', methods=['POST'])
#@login_required
def create_section():
    """
    Route used to create a section for a course.\n
    @author nouryehia
    """
    s_name = request.json['section_name']
    s_id = request.json['section_id']
    c_id = request.json['course_id']

    section = Section(section_name=s_name, section_id=s_id, course_id=c_id)
    Section.add_to_db(section)

    return jsonify({'reason': 'section created'}), 200

@section_api_bp.route('/find_all_in_course', methods=['GET'])
def find_all_in_course():
    """
    Route used to find all sections in a particular course by id.\n
    @author james-c-lars
    """

    course_id = request.args.get('course_id', type=int)
    s = [section.to_json() for section in Section.find_all_in_course(course_id)]

    return jsonify({'reason': 'sections returned', \
        'result': list(s)}), 200

@section_api_bp.route('/find_section', methods=['GET'])
def find_section():
    """
    Route used to find a sections by id.\n
    @author james-c-lars
    """

    section_id = request.args.get('section_id', type=int)
    section = Section.find_by_db_id(section_id)

    return jsonify({'reason': 'sections returned', \
        'result': section.to_json()}), 200