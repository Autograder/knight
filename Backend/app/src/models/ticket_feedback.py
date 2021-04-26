from __future__ import annotations
from operator import attrgetter
from enum import Enum
from ..utils.time import TimeUtil
from typing import List

from ...setup import db
from .course import Course
from .enrolled_course import EnrolledCourse
# from .user import User  # Pretending
# from .queue import Queue
# from .ticket import Ticket, Status
# from typing import List


class Rating(Enum):
    """
    The ratings for the feedback, with the following option --> Database
    value:\n
    BAD --> 0
    NEUTRAL --> 1
    GOOD --> 2
    """
    BAD = 0
    NEUTRAL = 1
    GOOD = 2


class TicketFeedback(db.Model):
    """
    The ticket_feedback model that is in the data base.
    Fields:\n
    id --> The id of the ticket_feedback, unique primary key.\n
    ticket_id --> The id of the ticket that this feedback is associated to.\n
    rating --> The rating to this ticket_feedback.\n
    feedback --> The actual written feedback. Nullable.\n
    submitted_date --> The time that this feedback is submited.\n
    is_annoymous --> Whether this ticket feedback is annoymous.\n
    @author Yixuanzhou
    """
    __tablename__ = 'TicketFeedback'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('Ticket.id'),
                          nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.String(255), nullable=True)
    submitted_date = db.Column(db.DateTime, nullable=False,
                               default=TimeUtil.get_current_time())
    ec_grader_id = db.Column(db.Integer, db.ForeignKey('EnrolledCourse.id'),
                             nullable=False)
    is_anonymous = db.Column(db.Boolean, nullable=False)

    def __init__(self, **kwargs):
        """
        The constructor of the ticket object.\n
        Inputs:\n
        ticket_id --> The id of the ticket that this feedback belongs to.\n
        rating --> The rating of the ticket.\n
        feedback --> The actual feedback content.\n
        submitted_date --> The time it is submited.\n
        is_annoymous --> Whether the feedback is left annoymously.\n
        Return:\n
        The created ticket feedback object
        """
        super(TicketFeedback, self).__init__(**kwargs)

    def save(self):
        """
        Save the object to the database.
        """
        db.session.commit()

    def to_json(self):
        """
        Return a json copy of the ticket feedback.
        """
        ret = {}
        ret['id'] = self.id
        ret['ticket_id'] = self.ticket_id
        ret['rating'] = Rating(self.rating).name
        ret['feedback'] = self.feedback
        ret['is_anonymous'] = self.is_anonymous
        ret['submitted_date'] = self.submitted_date
        return ret

    # Static add method
    @staticmethod
    def add_to_db(tf: TicketFeedback):
        """
        Add the queue to the database.\n
        Inputs:\n
        tf --> the ticketfeedback object created.\n
        """
        db.session.add(tf)
        db.session.commit()

    @staticmethod
    def get_ticket_feedback(ticket_id: int) -> TicketFeedback:
        """
        Given a ticket, return the ticket feedbacks
        Input:\n
        ticket_id --> The id of the ticket
        Returns:\n
        A list of tickect feedback related to that ticket.
        """
        ret = TicketFeedback.query.filter_by(ticket_id=ticket_id).first()
        return ret

    @staticmethod
    def add_feedback(ticket_id: int, rating: int, feedback: str,
                     anonymous: bool, ec_grader_id: int) -> TicketFeedback:
        """
        Add a ticket feedback to the db
        Inputs:\n
        ticket_id --> The id of the ticket.
        rating --> The rating of the feedback.
        feedback --> The feedback text.
        anonymous --> True of false.
        """
        fb = TicketFeedback(
            ec_grader_id=ec_grader_id,
            ticket_id=ticket_id,
            rating=rating,
            feedback=feedback,
            anonymous=anonymous,
            created_at=TimeUtil.get_current_time())
        TicketFeedback.add_to_db(fb)
        return fb

    @staticmethod
    def get_feedback_for_grader(queue_id: int,
                                user_id: int) -> List[TicketFeedback]:
        c_id = Course.get_course_by_queue_id(q_id=queue_id)
        ec_grader_id = EnrolledCourse.find_user_in_course(user_id=user_id,
                                                          course_id=c_id)
        ret = TicketFeedback.query.filter_by(ec_grader_id=ec_grader_id).\
            order_by(TicketFeedback.submitted_date.desc()).all()
        return ret
