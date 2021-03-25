# File name: __init__.py
# Author: @nouryehia
# Description: We imports our routes and register our blueprints here.

# Flask import
from .setup import app

# Import routes
from .src.apis.temp_user import user_api

# Register blueprints
app.register_blueprint(user_api, url_prefix='/api/user')
