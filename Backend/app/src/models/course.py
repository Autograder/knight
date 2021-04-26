from __future__ import annotations
from typing import Dict, List, Optional
from ...setup import db
from enum import Enum
# TODO: In the future, use Mihai's security stuffs.
# from ..security.roles import CRole
# from .section import Section


class Quarter(Enum):
    """
    Enum for quarters.
    Fields --> Database Value:\n
    FALL --> 0\n
    WINTER --> 1\n
    SPRING --> 2\n
    SS1 --> 3\n
    SS2 --> 4\n
    @author: mihaivaduva21
    """
    FALL = 0
    WINTER = 1
    SPRING = 2
    SS1 = 3
    SS2 = 4


class Course(db.Model):
    """
    Represents a course in the DB with relevant functions for
    manipulation of course data.
    Fields:
    id --> Course ID. Unique, primary key
    description --> Description of text
    name --> Name of the course
    quarter --> The quarter in which the course is held
    short_name --> Shortened name of the course
    year --> Year in which the course is held
    active --> boolean representing if the course is currently held.
    queue_enabled --> boolean representing if the queue is enabled or not.
    cse --> True if CSE course false otherwise
    lock_button --> true if queue enabled, false otherwise
    queue_id -->  Queue id, unique referencing Queue table
    @author:Mihai
    """
    __tablename__ = 'Course'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    quarter = db.Column(db.Integer, nullable=False)
    short_name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=True)
    year = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)
    queue_enabled = db.Column(db.Boolean, nullable=False, default=False)
    cse = db.Column(db.Boolean, nullable=False, default=True)
    lock_button = db.Column(db.Boolean, nullable=False, default=False)
    queue_id = db.Column(db.Integer, db.ForeignKey('Queue.id'), nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    instructor_id = db.Column(db.Integer,
                              db.ForeignKey('Users.id'), nullable=False)

    def __init__(self, **kwargs):
        """
        The constructor of the queue calendar object.\n
        """
        super(Course, self).__init__(**kwargs)

    def to_json(self) -> Dict[str, str]:
        '''
        Function that takes a course object and returns it in dictionary
        form. Used on the API layer.\n
        Params: none\n
        Returns: Dictionary of the user info
        '''
        ret = {}
        ret['id'] = self.id
        ret['description'] = self.description
        ret['name'] = self.name
        ret['quarter'] = Quarter(self.quarter).name
        ret['short_name'] = self.short_name
        ret['url'] = self.url
        ret['year'] = self.year
        ret['active'] = self.active
        ret['queue_enabled'] = self.queue_enabled
        ret['cse'] = self.cse
        ret['lock_button'] = self.lock_button
        ret['queue_id'] = self.queue_id
        ret['is_deleted'] = self.is_deleted
        ret['instructor_id'] = self.instructor_id
        return ret

    def save(self):
        """
        Save the object in the database.
        """
        db.session.commit()

    def __repr__(self) -> str:
        """
        repr
        """
        return 'course ' + str(self.year) + ' ' + self.short_name + ' ' + \
            str(self.quarter)

    def switch_queue_status(self):
        """
        Switches the status of the queue.
        """
        self.queue_enabled = not self.queue_enabled
        self.save()

    def switch_lock_status(self):
        """
        Switches the status of the lock.
        """
        self.lock_button = not self.lock_button
        self.save()

    def switch_active_status(self):
        """
        Switches the active status
        """
        self.active = not self.active
        self.save()

    def switch_cse(self):
        """
        Switch the value of the cse boolean
        """
        self.cse = not self.cse
        self.save()

    '''
    def get_sections(self) -> List[Section]:
        """
        Get the sections of a course
        """
        return Section.query.filter_by(course_id=self.id).all()
    '''

    # Get students / get instructors are already in enrolled course
    @staticmethod
    def get_course_by_id(course_id) -> Optional[Course]:
        """
        Returns a Course from a course id
        """
        return Course.query.filter_by(id=course_id).first()

    @staticmethod
    def get_course_by_queue_id(q_id) -> Optional[Course]:
        """
        Returns a Course from a queue id
        """
        return Course.query.filter_by(queue_id=q_id).first()

    @staticmethod
    def get_queue_id_by_id(course_id) -> Optional[int]:
        """
        Returns a queue_id from a course id
        """
        course = Course.query.filter_by(id=course_id).first()

        return course.queue_id if course else None

    def quarter_year(self) -> str:
        """
        Returns the quarter and the year.
        """
        if self.quarter == Quarter.FALL.value:
            return "FA" + str(self.year)
        elif self.quarter == Quarter.WINTER.value:
            return "WI" + str(self.year)
        elif self.quarter == Quarter.SPRING.value:
            return "SP" + str(self.year)
        elif self.quarter == Quarter.SS1.value:
            return "SS1" + str(self.year)
        elif self.quarter == Quarter.SS2.value:
            return "SS2" + str(self.year)

    def exists_course(quarter: int, short_name: str, year: int)\
            -> Optional[Course]:
        '''
        Function that tries to find a course by short name, quarter and year.
        Params: pid - string. email - string.\n
        Returns: Optional[Course] or None
        '''
        return Course.query.filter_by(quarter=quarter,
                                      short_name=short_name,
                                      year=year).first()

    @staticmethod
    def create_course(description: str, name: str, quarter: int,
                      short_name: str, url: str, year: int,
                      active: bool, queue_enabled: bool, cse: bool,
                      queue_id: int, instructor_id: int) -> Optional[Course]:

        """
        Creates a new course and adds it to the databease.
        """
        if Course.exists_course(quarter, short_name, year):
            return None

        course = Course(description=description, name=name, quarter=quarter,
                        short_name=short_name, url=url, year=year,
                        active=active, queue_enabled=queue_enabled, cse=cse,
                        lock_button=False, queue_id=queue_id,
                        instructor_id=instructor_id)
        db.session.add(course)
        course.save()
        return course

    @staticmethod
    def delete_course(short_name: str, quarter: int, year: int) -> bool:
        """
        Delete an entry from the enrolled_course table.\n
        Inputs:\n
        short_name --> The short_name of the course to delete.\n
        quarter --> The quarter of the course to delete.\n
        year --> The year of the course to delete.\n
        """
        course = Course.exists_course(quarter, short_name, year)
        if course:
            course.is_deleted = True
            course.save()
            return True
        else:
            return False

    @staticmethod
    def get_all_courses(quarter: int = None, year: int = None) -> List[Course]:
        """
        Get all the courses listed in incresing order by time created.
        Inputs:\n
        quarter --> Optional parameter for time period default None.
        year --> Optional parameter for time period must be specified when
                 quarter is specified.
        """
        if quarter:
            return Course.query.filter_by(quarter=quarter, year=year,
                                          is_deleted=False).all()
        elif year:
            return Course.query.filter_by(year=year, is_deleted=False).all()
        else:
            return Course.query.filter_by(is_deleted=False).all()