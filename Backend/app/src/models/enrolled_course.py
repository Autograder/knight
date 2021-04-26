from __future__ import annotations
from enum import Enum
from ...setup import db
from typing import List, Dict
from .course import Course
from .user import User


class Status(Enum):
    """
    Describe the corresponidng status of a user in the class (queue).
    The following fields are defined as name --> database value:\n
    Fields:\n
    ACTIVE --> 0\n
    INACTIVE --> 1\n
    BUSY --> 2\n
    @author: YixuanZhou
    """
    ACTIVE = 0
    INACTIVE = 1
    BUSY = 2


class Role(Enum):
    """
    All the roles that a user can have for a class.\n
    The following fields are difend as name --> database value:\n
    Fields --> Database Value:\n
    ROOT --> 0\n
    ADMIN --> 1\n
    INSTRUCTOR --> 2\n
    GRADER --> 3\n
    STUDENT --> 4\n
    @author: YixuanZhou
    """
    ROOT = 0
    ADMIN = 1
    INSTRUCTOR = 2
    GRADER = 3
    STUDENT = 4


class EnrolledCourse(db.Model):
    """
    The enrolled course database model.\n
    All students should be in the sections that is corresponding to their
    enrollment.\n
    All the instructors / tutors shoud be in a dummy section.\n
    When a student drop from the class, we should clear that row of entry by
    calling delete_enrolled_user.\n
    Fields: \n
    id --> The id of the queue, unique primary key.\n
    user_id --> Foreign key to the user id corresponding to this entry\n
    role --> The role of the user in this class.\n
    section_id --> The foreign key to the section id
                            at high capacity, not nullable.\n
    status --> The status of a user in the class.(mainly for tutor status)\n
    course_id --> The id of the coures that the user is enrolled in.\n
    @author YixuanZhou
    """
    __tablename__ = 'EnrolledCourse'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    role = db.Column(db.Integer, nullable=False, default=True)
    section_id = db.Column(db.Integer, db.ForeignKey('Section.section_id'),
                           nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('Course.id'),
                          nullable=False)
    status = db.Column(db.Integer, nullable=False, default=Status.INACTIVE)
    course_short_name = db.Column(db.String(255), nullable=False)

    def __repr__(self) -> str:
        """
        Return the string cancatenation of the user_id, role, section_id,
        course_id and status.\n
        Inputs:\n
        None\n
        Returns:\n
        A string representation of the enrolled_course object.\n
        """
        return "user_id: " + str(self.user_id) + " role: " + str(self.role) +\
               " section_id " + str(self.section_id) + " course_id " +\
               str(self.course_id) + " status: " + str(self.status) +\
               " course_short_name: " + str(self.course_short_name)

    def __eq__(self, other):
        """
        Override the comparison functions of the objects.\n
        Inputs:\n
        The other object of the same type to compare.\n
        Returns:\n
        True if their user_id are the same, meaning they represents the same
        objects.\n
        False otherwise.\n
        """
        if isinstance(other, self.__class__):
            return self.user_id == other.user_id
        else:
            return False

    def __hash__(self):
        """
        The has method for the object, we hash the user_id field.\n
        Returns:\n
        The hash result for the user_id field.\n
        """
        return hash(self.user_id)

    def to_json(self) -> Dict[str, str]:
        '''
        Function that takes a user object and returns it in dictionary
        form. Used on the API layer.\n
        Params: none\n
        Returns: Dictionary of the user info
        '''
        ret = {}
        ret['user_id'] = self.user_id
        ret['course_id'] = self.course_id
        ret['section_id'] = self.section_id
        ret['id'] = self.id
        ret['status'] = Status(self.status).name
        ret['role'] = Role(self.role).name
        ret['course_short_name'] = self.course_short_name
        return ret

    def get_role(self) -> Role:
        """
        Get the role of this EnrolledCourse entry.\n
        Return:\n
        The Role type.
        """
        return self.role

    def get_status(self) -> Role:
        """
        Get the role of this EnrolledCourse entry.\n
        Return:\n
        The Role type.
        """
        return self.status

    def change_role(self, role: Role) -> bool:
        """
        Change the role of the user in this class.\n
        Inputs:\n
        role --> The role to change.\n
        Return:\n
        Whether the change is successed.
        """
        self.role = role.value
        self.save()
        return True

    def change_status(self, status: Status) -> bool:
        """
        Change the status of the user in this class.\n
        Inputs:\n
        status --> The status to change.\n
        Return:\n
        Whetehr the change is successed.
        """
        self.status = status.value
        self.save()
        return True

    def find_students_in_section(self, given_id: int):
        user_ids = []
        students = []

        records = EnrolledCourse.query.filter_by(section_id=given_id).all()
        for rec in records:
            user_ids.add(rec.user_id)

        for id in user_ids:
            student = User.get_user_by_id(id)
            students.add(student.first_name + " " + student.last_name)

        return students

    def save(self):
        """
        Update the object to the database.\n
        """
        db.session.commit()

    @staticmethod
    def get_ec_by_id(ec_id: int) -> EnrolledCourse:
        """
        Get ec entry by id
        """
        return EnrolledCourse.query.filter_by(id=id).first()

    @staticmethod
    def enroll_user(enrolled_user: EnrolledCourse) -> bool:
        """
        Add an enrolled user into the course.\n
        Inputs:\n
        enrolled_user --> The EnrolledCourse object to add.\n
        Return:\n
        Whether the user is added.
        """
        db.session.add(enrolled_user)
        db.session.commit()
        return True

    @staticmethod
    def enroll_user_to(user_id: int, course_id: int,
                       section_id: int, role: Role) -> bool:
        """
        Enroll a student to a course with corresponding sections.\n
        All the non-student users should be enrolled in to a dummy section.\n
        Inputs:\n
        user_id --> The user_id of the user to enroll.\n
        course_id --> The course_id that the user is enrolled to.\n
        section_id --> The section_id object that the user is enrolled to.\n
        role --> The role of the user in the class.\n
        Return:\n
        Whether the user is added.
        """
        ec = EnrolledCourse.find_user_in_course(user_id=user_id,
                                                course_id=course_id)
        if ec:
            return False

        course_short_name = Course.get_course_by_id(course_id).short_name

        enroll_student = EnrolledCourse(user_id=user_id,
                                        role=role,
                                        section_id=section_id,
                                        status=Status.ACTIVE.value,
                                        course_id=course_id,
                                        course_short_name=course_short_name)
        return EnrolledCourse.enroll_user(enroll_student)

    @staticmethod
    def find_user_in_course(user_id: int,
                            course_id: int) -> EnrolledCourse:
        """
        Find a user which is in a specific course.\n
        Inputs:\n
        user_id --> The User id to search for.\n
        course_id --> The Course id to search for.\n
        Return:\n
        A enrolled course entry of the particular user.\n
        """
        return EnrolledCourse.query.filter_by(course_id=course_id,
                                              user_id=user_id).first()

    @staticmethod
    def find_all_user_in_section(course_id: int, section_id: int)\
            -> List[EnrolledCourse]:
        return EnrolledCourse.query.filter_by(course_id=course_id,
                                              section_id=section_id).all()

    @staticmethod
    def find_all_user_in_course(course_id: int,
                                role: List[Role] = None) \
            -> (bool, List[EnrolledCourse]):
        """
        Get a list of all the entries corresponding a course.\n
        There can be extra parameter provided which is role.\n
        Inputs:\n
        course --> The Course object to look for.\n
        role --> (Optional) the role to look for.\n
        """
        c = Course.get_course_by_id(course_id)
        if not c:
            return False, None
        if not role:
            return True, EnrolledCourse.query.filter_by(course_id=course_id).\
                order_by(EnrolledCourse.id.desc()).all()
        else:
            return True, EnrolledCourse.\
                query.filter_by(course_id=course_id).\
                filter(EnrolledCourse.role.in_(role)).\
                order_by(EnrolledCourse.id.desc()).all()

    @staticmethod
    def find_courses_user_in(user_id: int,
                             role: List[Role] = None) \
            -> List[EnrolledCourse]:
        """
        Get a list of all the entries corresponding a user.\n
        There can be extra parameter provided which is role.\n
        Inputs:\n
        user --> The User object to look for.\n
        role --> (Optional) the role to look for.\n
        """
        if not role:
            return EnrolledCourse.query.filter_by(user_id=user_id).all()
        else:
            return EnrolledCourse.query.\
                filter_by(user_id=user_id).\
                filter(EnrolledCourse.role.in_(role)).all().\
                order_by(EnrolledCourse.id.desc()).all()

    @staticmethod
    def find_active_tutor_for(queue_id: int) -> (bool, str, List[User]):
        """
        Find all the active tutor for a given queue object.\n
        Inputs:\n
        The Queue object to search for.\n
        Returns:\n
        A list of active tutors User objects. Could have null entries\n
        """
        course = Course.get_course_by_queue_id(queue_id)
        if not course:
            return (False, 'Course not found', None)
        grader_enrolled_course = EnrolledCourse.query\
            .filter_by(role=Role.GRADER.value, course_id=course.id,
                       status=Status.ACTIVE.value).all()
        # Since each tutor might be enrolled in multiple sections,
        # we remove the duplicates here.

        grader_set = set()
        grader_set.update(grader_enrolled_course)
        return (True, 'success',
                [User.get_user_by_id(grader.id)
                    for grader in list(grader_set)])

    @staticmethod
    def delete_enrolled_user_from_course(user_id: int, course_id: int) -> bool:
        """
        Delete an entry from the enrolled_course table.\n
        Inputs:\n
        user_id --> The user_id of the user to delete.\n
        course_id --> The course_id of the course to delete user from.\n
        """
        enrolled_user = EnrolledCourse.find_user_in_course(user_id=user_id,
                                                           course_id=course_id)
        if enrolled_user:
            db.session.delete(enrolled_user)
            db.session.commit()
            return True
        else:
            return False

    '''
    Was in User model, but should not be needed anymore as same result can be
    obtained by calling find_user_in_all_course directly. Keeping it here just
    in case though.
    '''
    # @staticmethod
    # def get_courses_for_user(self) -> List[EnrolledCourse]:
    #    '''
    #    Database query for getting all EnrolledCourses for our user.\n
    #    Params: None\n
    #    Returns: A list of EnrolledCourses (can be empty)
    #    '''
    #    return EnrolledCourse.find_user_in_all_course(self.id)
