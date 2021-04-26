from __future__ import annotations
from typing import List

from enum import Enum
from ...utils.time import TimeUtil

from ....setup import db
from ..user import User
# from ..queue import Queue


class EType(Enum):
    """
    The enum of login events with the following
    option --> database value:\n
    LOGIN --> 0\n
    LOGOUT --> 1 \n
    @author YixuanZhou
    """
    LOGIN = 0
    LOGOUT = 1


class ActionType(Enum):
    """
    The enum of the action type of this login event with
    option --> database value:\n
    MANUAL --> 0\n
    AUTOMATIC --> 1\n
    @author YixuanZhou
    """
    MANUAL = 0
    AUTOMATIC = 1


class QueueLoginEvent(db.Model):
    """
    The Queue Login Event model in the database.\n
    event_type --> The type of the event.\n
    action_type --> The action type of the event (auto or man).\n
    timestamp --> The time of the action related this event, default now.\n
    grader_id --> The id of the tutor who triggered this event, forign key\n
    queue_id --> The id of the queue that the events are related to.\n
    @author YixuanZhou
    """
    __tablename__ = 'QueueLoginEvent'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    event_type = db.Column(db.Integer, nullable=False)
    action_type = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False,
                          default=TimeUtil.get_current_time())
    grader_id = db.Column(db.Integer, db.ForeignKey('EnrolledCourse.id'),
                          nullable=False)
    queue_id = db.Column(db.Integer, db.ForeignKey('Queue.id'), nullable=False)

    def __init__(self, **kwargs):
        """
        The constractor of the QueueLoginEvent.\n
        Inputs:\n
        event_type --> The type of the event.\n
        action_type --> The type of the action related this event.\n
        timestamp --> The time of this event that happenes.\n
        grader_id --> The grader's id that created this event.\n
        """
        super(QueueLoginEvent, self).__init__(**kwargs)

    # Bool query methods of Queue Login Event
    def is_manual(self) -> bool:
        """
        Whether the action type is manual.\n
        Returns:\n
        A bool indicates if it is manual or not.\n
        """

        return self.action_type == ActionType.MANUAL

    def is_automatic(self) -> bool:
        """
        Whether the action type is automatic.\n
        Returns:\n
        A bool indicates if it is automatic or not.\n
        """
        return self.action_type == ActionType.AUTOMATIC

    def find_event_in_range(self, queue_id: int, start: str,
                            end: str = TimeUtil.get_current_time(),
                            grader: User = None):
        """
        Get all the queue login events for a queue in a given range.\n
        Inputs:\n
        queue --> The queue object to look for.\n
        start --> The datetime object of the time to start looking for\n
        end --> The datetime objec tof the time to end looking for
        (default = now).\n
        grader --> The grader to serch for (Optional if wanted).\n
        Returns:\n
        A list of the queue login event objects that is associsated with the
        given queue for a given range of time.\n
        """
        if (grader is not None):
            event_list = QueueLoginEvent.query().filter_by(queue_id=queue_id)\
                        .order_by(QueueLoginEvent.timestamp).desc.all()
        else:
            event_list = QueueLoginEvent.query()\
                         .filter_by(queue_id=queue_id,
                                    grader_id=grader.id)\
                         .order_by(QueueLoginEvent.timestamp).desc.all()
        return list(filter(lambda x: start <= x.closed_at <= end, event_list))

    # Static add method
    @staticmethod
    def get_event_timestamp(qle: QueueLoginEvent) -> str:
        return qle.timestamp

    def add_to_db(self):
        """
        Add the queue login event to the database.\n
        Inputs:\n
        qle --> the QueueLoginEvent object created.\n
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def find_login_time_for_user(grader: User) -> List[QueueLoginEvent]:
        elist = QueueLoginEvent.query().filter_by(grader_id=grader.id).all()
        sorted_elist = elist.sort(key=QueueLoginEvent.get_event_timestamp)
        return sorted_elist

    @staticmethod
    def create_login_event(event_type: EType, action_type: ActionType,
                           grader_id: int, queue_id: int,
                           timestamp=TimeUtil.get_current_time()):
        qevt = QueueLoginEvent(event_type=event_type.value,
                               action_type=action_type,
                               grader_id=grader_id, queue_id=queue_id,
                               timestamp=TimeUtil.convert_str_to_datetime(timestamp))
        qevt.add_to_db()

