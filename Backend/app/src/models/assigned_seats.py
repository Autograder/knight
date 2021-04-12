# needed for annotating return types of the same object
from __future__ import annotations

from typing import Dict, Tuple, Optional, List

from ...setup import db


class AssignedSeats(db.Model):
    """
    Represents an assignment of seats to students for a test of lab.\n
    Fields:
    id --> AssignedSeats ID. Unique, primary key\n
    assignment_name --> The name of this test or lab. A Unique identifying
    string.\n
    layout_id --> The layout these students are assigned to.\n
    section_id --> The section these students are in.\n
    course_id --> The course these students are in.\n
    seat_assignments --> A JSON String dictionary mapping seats to students.\n
    @author: james-c-lars
    """
    __tablename__ = 'AssignedSeats'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    assignment_name = db.Column(db.String(255), nullable=False)
    layout_id = db.Column(db.Integer,
                          db.ForeignKey('SeatingLayouts.id'),
                          nullable=False)
    section_id = db.Column(db.Integer,
                           db.ForeignKey('Section.id'),
                           nullable=False)
    course_id = db.Column(db.Integer,
                          db.ForeignKey('Course.id'),
                          nullable=False)
    seat_assignments = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        """
        Returns a String representing the seat assignment.\n
        """
        return f"Seating Layout - assignment_name:{self.assignment_name}, \
                 layout_id:{self.layout_id}, \
                 section_id:{self.section_id}, \
                 course_id:{self.course_id}, \
                 seat_assignments:{self.seat_assignments}"

    def save(self) -> None:
        '''
        Saves the current object in the DB.\n
        Params: None\n
        Returns: None
        '''
        db.session.commit()

    def to_json(self) -> Dict[str, str]:
        '''
        Function that takes a user object and returns it in dictionary
        form. Used on the API layer.\n
        Params: none\n
        Returns: Dictionary of the user info
        '''
        ret = {}
        ret['id'] = self.id
        ret['assignment_name'] = self.assignment_name
        ret['layout_id'] = self.layout_id
        ret['section_id'] = self.section_id
        ret['course_id'] = self.course_id
        ret['seat_assignments'] = self.seat_assignments
        return ret

    @staticmethod
    def create_assignment(assignment_name: str, layout_id: int,
                          section_id: int, course_id: int,
                          seat_assignments: str) -> Tuple[bool, AssignedSeats]:
        '''
        Function that creates a new assigned seats object and adds it to
        the database.\n
        Params: assignment_name - str, layout_id - int, section_id - int
        , course_id - int, seat_assignments - str.\n
        Returns: boolean value for whether the assignment_name already existed,
        and a AssignedSeats object if the creation was successful.
        '''

        # don't try to add a preexisting assignment
        if AssignedSeats.find_by_name(assignment_name):
            return False, None

        sa = AssignedSeats(assignment_name=assignment_name,
                           layout_id=layout_id, section_id=section_id,
                           course_id=course_id,
                           seat_assignments=seat_assignments)
        db.session.add(sa)
        sa.save()
        return True, sa

    @staticmethod
    def find_by_name(assignment_name: str) -> Optional[AssignedSeats]:
        '''
        Function that tries to find a seat assignment via the name it
        was given.

        Note that this function may return `None` if the given name
        doesn't map to any known seat assignments.\n
        Params: location - string.\n
        Returns: Optional[AssignedSeats]
        '''
        return AssignedSeats.query.filter_by(assignment_name=assignment_name
                                             ).first()

    @staticmethod
    def get_all_assignments() -> List[AssignedSeats]:
        '''
        Function that returns a list of all seat assignments in the database.\n
        Params: None\n
        Returns: List[AssignedSeats]
        '''
        return AssignedSeats.query.all()

    @staticmethod
    def get_assignment_by_id(assignment_id: db.Integer
                             ) -> Optional[AssignedSeats]:
        '''
        Function that retrieves a seat assignment via the id.\n
        Params: `assignment_id` - assignment ID in the DB.\n
        Returns: Optional[AssignedSeats]
        '''
        return AssignedSeats.query.filter_by(id=assignment_id).first()

    @staticmethod
    def get_assignments_by_course_id(course_id: db.Integer
                                     ) -> List[AssignedSeats]:
        '''
        Function that retrieves a seat assignment via the course id.\n
        Params: `course_id` - course ID in the DB.\n
        Returns: List[AssignedSeats]
        '''
        return AssignedSeats.query.filter_by(course_id=course_id)

    @staticmethod
    def get_assignments_by_section_id(section_id: db.Integer
                                      ) -> List[AssignedSeats]:
        '''
        Function that retrieves a seat assignment via the section id.\n
        Params: `section_id` - section ID in the DB.\n
        Returns: List[AssignedSeats]
        '''
        return AssignedSeats.query.filter_by(section_id=section_id)
