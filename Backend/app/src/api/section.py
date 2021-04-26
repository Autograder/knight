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