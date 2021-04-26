from __future__ import annotations

from ....setup import db
from enum import Enum
from ...utils.time import TimeUtil
from ..enrolled_course import EnrolledCourse, Role
from ..course import Course


class EventType(Enum):
    """
    All the event that can happen to a ticket with the \
        following options --> database value:\n
    CREATED --> 0
    ACCEPTED --> 1
    RESOLVED --> 2
    UPDATED --> 3
    DEFERED --> 4
    CANCELED --> 5
    COMMENTED --> 6
    """
    CREATED = 0
    ACCEPTED = 1
    RESOLVED = 2
    UPDATED = 3
    DEFERRED = 4
    CANCELED = 5
    COMMENTED = 6


class TicketEvent(db.Model):
    """
    The event happened on ticket.\n
    Fields:\n
    id --> The id of the ticket, unique primary key.\n
    event_type --> The type of this event.\n
    ticket_id --> The ticket associated with this event, forien key.\n
    message --> The message associated with this event, nullable.\n
    is_private --> Whether this update is anonymous.\n
    ec_user_id --> EC id of user that created this event.\n
    timestamp --> The timestamp of this event.\n
    @authour: YixuanZ
    """
    __tablename__ = 'TicketEvent'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    # need to change a name in db, since type is a presereved word in python
    event_type = db.Column(db.Integer, nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('Ticket.id'),
                          nullable=False)
    message = db.Column(db.String(255), nullable=True)
    is_private = db.Column(db.Boolean, nullable=False)
    ec_user_id = db.Column(db.Integer, db.ForeignKey('EnrolledCourse.id'),
                           nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False,
                          default=TimeUtil.get_current_time())

    def __init__(self, **kwargs):
        super(TicketEvent, self).__init__(**kwargs)

    # Getter Methods
    def is_create(self) -> bool:
        """
        Check if the event type is create.\n
        Return:\n
        Bool indicating if it its create type.\n
        """
        return self.event_type == EventType.CREATED

    def is_accepted(self) -> bool:
        """
        Check if the event type is accepted.\n
        Return:\n
        Bool indicating if it its accepted type.\n
        """
        return self.event_type == EventType.ACCEPTED

    def is_resolved(self) -> bool:
        """
        Check if the event type is resolved.\n
        Return:\n
        Bool indicating if it its resolved type.\n
        """
        return self.event_type == EventType.RESOLVED

    def is_update(self) -> bool:
        """
        Check if the event type is update.\n
        Return:\n
        Bool indicating if it its update type.\n
        """
        return self.event_type == EventType.UPDATED

    def is_deffered(self) -> bool:
        """
        Check if the event type is deffered.\n
        Return:\n
        Bool indicating if it its deffered type.\n
        """
        return self.event_type == EventType.DEFERRED

    def is_canceled(self) -> bool:
        """
        Check if the event type is canceled.\n
        Return:\n
        Bool indicating if it its canceled type.\n
        """
        return self.event_type == EventType.CANCELED

    def is_commented(self) -> bool:
        """
        Check if the event type is commented.\n
        Return:\n
        Bool indicating if it its commeneted type.\n
        """
        return self.event_type == EventType.COMMENTED

    def to_json(self) -> dict:
        """
        Return a dict representation of the object.
        """
        ret = {}
        ret['id'] = self.id
        ret['event_type'] = EventType(self.event_type).name
        ret['ticket_id'] = self.ticket_id
        ret['message'] = self.message
        ret['is_private'] = self.is_private
        ret['ec_user_id'] = self.ec_user_id
        ret['timestamp'] = self.timestamp
        return ret

    def reveal_user(self, user_id: int, course_id: int) -> bool:
        """
        Determine whether this event can be revealed to a user.\n
        Inputs:\n
        user --> The user object to be determined.\n
        course --> The course of this user & of this ticket is in.\b
        Return:\n
        bool value of whether this can be viewed by this user.\n
        """
        ec = EnrolledCourse.find_user_in_course(user_id=user_id,
                                                course_id=course_id)
        origin_event = TicketEvent.query.filter_by(id=self.id).\
            order_by(TicketEvent.timestamp.desc()).first()

        if not self.is_private:
            return True
        elif ec.role > Role.STUDENT.value:
            return True
        elif origin_event.ec_user_id == ec:
            return True
        else:
            return False

    def add_to_db(self):
        """
        Add the ticket to the database.\n
        Inputs:\n
        ticket --> the ticket object created.\n
        """
        db.session.add(self)
        db.session.commit()

    # Static add method
    @staticmethod
    def create_event(event_type: EventType, ticket_id: int,
                     message: str, is_private: bool,
                     user_id: int, queue_id: int) -> TicketEvent:
        """
        Create a ticket event
        event_type --> The type of this event
        ticket_id --> The id of the ticket the event is to
        message --> The message of this event
        is_private --> Whether this event is private (should in sync to ticket)
        user_id --> The id of the user to create this event.
        """
        cid = Course.get_course_by_queue_id(queue_id).id
        ec = EnrolledCourse.find_user_in_course(user_id=user_id,
                                                course_id=cid).id

        evt = TicketEvent(event_type=event_type.value, ticket_id=ticket_id,
                          message=message, is_private=is_private,
                          ec_user_id=ec, timestamp=TimeUtil.get_current_time())
        evt.add_to_db()
        return evt

    @staticmethod
    def get_events_for_tickets(user_id: int, course_id: int,
                               ticket_id: int) -> dict:
        """
        Get all evenst for a ticket.\n
        Inputs:\n
        user_id: the id of the user making this request.\n
        course_id: the id of the course in which this request is made.\n
        ticket_id: the id of the ticket to search for.\n
        Results:\n
        A dict of ticket events.
        """
        event_list = TicketEvent.query.filter_by(ticket_id=ticket_id).\
            order_by(TicketEvent.timestamp.desc()).all()
        ret = []
        for event in event_list:
            if not event.reveal_user(user_id=user_id, course_id=course_id):
                continue
            ret.append(event.to_json())
        return ret

    @staticmethod
    def get_all_ticket_events():
        """
        For testing use
        """
        evts = TicketEvent.query.all()
        return evts
