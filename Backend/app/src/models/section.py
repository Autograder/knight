from __future__ import annotations

from ...setup import db


class Section (db.Model):
    """
    Represents a section in the DB with relevant functions for
    creating a section, adding users to it, sorting the members in a
    section so that their grades can be released, and finding a section
    by its id.\n
    IMPORTANT NOTE: Everytime a section is used if it was not just
    constructed, update_section must be called. Also you must make sure a
    course exists before you try to create a section.\n
    Fields:
    id --> Section ID within table. Unique, primary key.\n
    section_name --> Section name.\n
    section_id --> Section id (webreg id - may not be unique).\n
    course_id --> Course id to the course that the section is in.
    Foreign key to courses table.\n
    @author: sccontre\n
    """

    __tablename__ = 'Section'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    section_name = db.Column(db.String(255), nullable=False)
    section_id = db.Column(db.Integer, nullable=False, unique=True)
    course_id = db.Column(db.Integer, db.ForeignKey('Course.id'),
                          nullable=False)

    def __init__(self, **kwargs):
        '''
        Constructs the section object by delegating to Model. Also creates
        a class variable that holds the names of all of the students within
        the course so that the students can be listed\n
        Params: None.\n
        Returns: None.\n
        '''

        # Initialize the object
        super(Section, self).__init__(**kwargs)
        """
        # Find all the students in the section using a database query
        # that returns a set of strings in the format of "First Last"
        self.students_in_section =\
            EnrolledCourse.find_students_in_section(self.id)
        """

    def __repr__(self):
        '''
        Returns the name of the section.\n
        Params: None.\n
        Returns: Name of the section.\n
        '''

        return self.section_name

    def to_json(self):
        '''
        Return a json representation of the current section.
        @author: YixuanZ
        '''
        ret = {}
        ret['id'] = self.id
        ret['section_id'] = self.section_id
        ret['course_id'] = self.course_id
        ret['section_name'] = self.section_name
        
        return ret

    # TODO: We dont need this method since section do not store students.
    '''
    def update_section(self):
        Updates the object's instance field students_in_section so that any
        added or dropped students are filled into the set. Important because
        python does not allow these instance fields to be kept after an object
        goes out of scope.\n
        Params: None.\n
        Returns: Self.\n
        # Find all the students in the section by delegating to EnrolledCourse
        updated_students_in_section =\
            EnrolledCourse.find_students_in_section(self.id)
        # Clear old set of students in section
        self.students_in_section.clear()
        # Update set of students
        for student in updated_students_in_section:
            self.students_in_section.add(student)
        return self
    '''

    # TODO: Sorting students by alphbetical order is a great, will in EC
    '''
    def sort_students(self, set_of_students: set):
        Sorts a set of students alphabetically so that they can be printed out
        whenever we want a list of students.\n
        This list of students does not have to be all the students in the
        section hence the parameter that can be passed as a different list.\n
        If you want to get a list of all of the students in the section, simply
        call this function with param Section.students_in_section.\n
        Params: A set of student names (strings) that needs to be sorted and
        passed back.\n
        Returns: Ordered list of students.\n
        # Create a list out of the set
        to_be_sorted = list(set_of_students)
        # Sort list alphabetically because it is simply a set of strings and
        # return the result
        to_be_sorted.sort()
        return to_be_sorted
    '''

    @staticmethod
    def find_by_id(section_id: int, course_id: int):
        '''
        Performs a database query by the course and section id.\n
        Params: None.\n
        Returns: The section if it is found, none otherwise.\n
        '''

        # Filter by section id and course id because section_id is not unique
        # on its own - return the first (and only) occurrence in table
        section = Section.query.\
            filter_by(section_id=section_id, course_id=course_id).first()

        return section

    @staticmethod
    def find_by_db_id(section_id: int):
        '''
        Performs a database query by the Section.id.\n
        Params: Section.id\n
        Returns: The section if it is found, none otherwise.\n
        @author james-c-lars
        '''

        section = Section.query.filter_by(id=section_id).first()
        
        return section

    @staticmethod
    def add_to_db(section: Section):
        """
        Adds a ticket to the database.\n
        Param: section --> the section object being added\n
        Returns: None.
        """
        db.session.add(section)
        db.session.commit()
    
    @staticmethod
    def find_all_in_course(course_id: int):
        '''
        Performs a database query by the course id.\n
        Params: course_id\n
        Returns: The list of sections under that course\n
        @author: james-c-lars
        '''
        return Section.query.filter_by(course_id=course_id).all()