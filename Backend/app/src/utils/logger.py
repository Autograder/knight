import logging
from typing import List
from threading import Lock

from ..models.user import User
from ..models.course import Course
from ..models.enrolled_course import Role
from .exceptions import SingletonAccessException



class LogLevels(object):
    '''
    Small class for making the logging levels visible
    from other classes without importing the `logging` python
    module.\n
    @author npcompletenate
    '''
    CRIT = logging.CRITICAL
    ERR = logging.ERROR
    WARN = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


class Logger(object):
    '''
    Class used for logging messages.\n
    @author npcompletenate & mihaivaduva
    '''

    __instance = None

    @staticmethod
    def get_instance():
        if Logger.__instance is None:
            with Lock():
                if Logger.__instance is None:
                    Logger()
        return Logger.__instance

    def __init__(self, level: int = logging.INFO):
        '''
        Initializes a logger object. Should not be run from outside of this
        class, as the logger is a singleton.
        params:
                level - log level to use. defaults to INFO
        '''
        if Logger.__instance is not None:
            raise SingletonAccessException("This class is a singleton!")

        filename = 'application.log'
        filemode = 'w'
        fmat = "%(asctime)s;%(levelname)s;%(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"

        # initialize the logger
        logging.basicConfig(
            level=level,
            format=fmat,
            filename=filename,
            filemode=filemode,
            datefmt=datefmt
            )
        self.log = logging.getLogger()
        Logger.__instance = self


    def logged_in(self, u: User) -> None:
        '''
        Writes log message for when a user logs in.\n
        params:
                u - logged in user
        '''
        message = f"User {u} with user id: {u.id} and email {u.email} " +\
            "logged in."
        self.log.debug(message)

    def reset_password(self, email: str) -> None:
        '''
        Writes log message for a password reset event.\n
        params: email - the email of the account resetting its password
        '''
        message = f"Account with email {email} reset password."
        self.log.info(message)

    def forgot_password(self, email: str) -> None:
        '''
        Writes log message for a password reset event.\n
        params: email - the email of the account receiving its password
        '''
        message = f"Account with email {email} forgot password and received" +\
            " a random password."
        self.log.info(message)

    def add_students_section(self, names: List[str], section: str, crse: str):
        '''
        Writes a log message for when students are added to a course section.\n
        params:
                names - list of strings of student names
                section - which section they're being added to
                crse - which course the section belongs to
        '''
        message = []
        message.append("Added the following students to ")
        message.append(section)
        message.append(" section of ")
        message.append(crse)
        message.append(" course: \n")
        for cnt, name in enumerate(names):
            message.append("-- " + name)

            # jank way of making sure the last entry doesn't have a newline
            if cnt != len(names) - 1:
                message.append("\n")

        self.log.info(''.join(message))

    def create_user(self, u: User) -> None:
        '''
        Log message for user account creation.\n
        params:
                u - User object added to the DB
        '''
        message = f"Created account {u} + with email {u.email}."
        self.log.info(message)

    def create_user_exist(self, email: str) -> None:
        '''
        Log message for repeat user creation
        '''
        message = f"Attempted to create account for email {email}" + \
            " but an account exists already."
        self.log.error(message)

    def create_course(self, c: Course) -> None:
        '''
        Log messsage for new course creation.\n
        params:
                c - Course object added to the DB
        '''
        message = f"Created course {c}."
        self.log.info(message)


    def added_section(self, sctn_name: str, course_id: int) -> None:
        '''
        Message for when a course is added to a section
        '''
        message = f"Added section: {sctn_name} to " + \
            f"course with id: {str(course_id)}."
        self.log.info(message)

    def changed_role(self, user_id: int, course_id: int, prev_role: Role,
                     new_role: Role) -> None:
        '''
        Message for when a user's role is changed.\n
        params:
                user_id - id in the DB for the user
                course_id - id in the DB for the course
                prev_role - User's previous role
                new_role - User's new role
        '''
        message = f"Changed role of user with ID: {str(user_id)}" + \
            f" for course with ID: {str(course_id)} from {prev_role}" + \
            f" to {new_role}."
        self.log.info(message)

    def created_ticket(self, user_id: int, course_id: int):
        '''
        Message for ticket creation.\n
        params:
                user_id - id for the user in the DB who created the ticket
                course_id - course id in the DB for the ticket
        '''
        message = f"User with ID: {str(user_id)} created ticket for course" +\
            f" with ID: {str(course_id)}."
        self.log.debug(message)

    def custom_msg(self, msg: str, level: int = logging.DEBUG) -> None:
        '''
        Logs a custom message.
        params:
                msg - message to log
                level - what logging level to use. If not given, defaults to
                DEBUG
        '''
        self.log.log(level, msg)
