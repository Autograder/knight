# File name: __init__.py
# Author: @nouryehia
# Description: We imports our routes and register our blueprints here.

# Flask import
from .setup import app

# Import routes
from .src.api.user import user_api_bp as uapi
from .src.api.seating_layout import seating_layout_api_bp as saapi
from .src.api.assigned_seats import assigned_seats_api_bp as asapi
from .src.api.course import course_api_bp as capi
from .src.api.section import section_api_bp as sapi
from .src.api.queue import queue_api_bp as qapi

# Register blueprints
app.register_blueprint(uapi, url_prefix="/api/users")
app.register_blueprint(saapi, url_prefix="/api/seating_layout")
app.register_blueprint(asapi, url_prefix="/api/assigned_seats")
app.register_blueprint(capi, url_prefix="/api/course")
app.register_blueprint(sapi, url_prefix="/api/section")
app.register_blueprint(qapi, url_prefix="/api/queue")
