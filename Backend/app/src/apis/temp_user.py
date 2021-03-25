# File name: temp_user.py
# Author: @nouryehia
# Description: Defines a temporary user API that can be deleted once the 1st
# real model/API is written.

from flask_cors import CORS  # Allow cross-origin ressource sharing
from flask import Blueprint, request, jsonify  # Flask libraries

from ..models.temp_user import User  # User model

# Create the blueprint
user_api = Blueprint('user_api', __name__)
CORS(user_api, supports_credentials=True)


# Route name: get_name
# Author: @nouryehia
# Description: Gets the name of user with passed in id
# Expected Param: 'user_id' - id of user we want to retrieve.
# Response:
# - If id exists: {'reason': 'success', 'result': < name of user > }
# - If id doesn't exist: {'reason': 'error', 'result': None }
@user_api.route('/get_name', methods=['GET'])
def get_name():
    user_id = request.args.get('user_id', type=int)  # Get param
    user = User.get_user_by_id(user_id=user_id)  # Get user

    if user:
        name = user.first_name + " " + user.last_name  # Get full name
        return jsonify({'reason': 'success', 'result': name}), 200
    else:
        return jsonify({'reason': 'error', 'result': None}), 400
