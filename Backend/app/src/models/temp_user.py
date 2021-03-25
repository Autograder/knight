# File name: temp_user.py
# Author: @nouryehia
# Description: Defines a temporary user model that can be deleted once the 1st
# real model/API is written.

from __future__ import annotations  # Needed to reference type in class
from typing import Optional  # Needed for optional returns
from ...setup import db  # Reference to database instance


# Class name: User
# Author: @nouryehia
# Description: Contains the User model
class User(db.Model):
    __tablename__ = 'Users'  # Name of table in database

    # Database fields
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    pid = db.Column(db.String(10), nullable=True, unique=True)
    last_login = db.Column(db.DateTime, nullable=True)
    urole = db.Column(db.Integer, nullable=False, default=2)
    request = db.Column(db.Boolean, nullable=False, default=False)
    token = db.Column(db.String(255), nullable=False, default="")

    # Method name: save
    # Author: @nouryehia
    # Description: Saves the current object in the database.
    # Params: None.
    # Returns: None.
    def save(self) -> None:
        db.session.commit()

    # Method name: get_user_by_id
    # Author: @nouryehia
    # Description: Uses database id to retrieve a user from database.
    # Params: user_id - The id of the user we want to retrieve.
    # Returns:
    # - User object if id exists in database.
    # - None otherwise
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        return User.query.filter_by(id=user_id).first()
