# File name: __init__.py
# Author: @nouryehia
# Description: We imports our routes and register our blueprints here.

# Flask import
from .setup import app

# Import routes
from .src.apis.temp_user import user_api
from .src.apis.seating_layout import seating_layout_api_bp as saapi
from .src.apis.assigned_seats import assigned_seats_api_bp as asapi

# Register blueprints
app.register_blueprint(user_api, url_prefix='/api/user')
app.register_blueprint(saapi, url_prefix="/api/seating_layout")
app.register_blueprint(asapi, url_prefix="/api/assigned_seats")
