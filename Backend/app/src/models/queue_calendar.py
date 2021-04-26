from __future__ import annotations

from typing import List, Dict

from ...setup import db


class QueueCalendar(db.Model):
    """
    The queue calendar model in the database.\n
    Fields:\n
    id --> The id of the queue calendar, primary key.\n
    url --> The url to the actual calendar.\n
    color --> The color of this calendar to be displayed.\n
    is_enabled --> Whether this calendar is enabled.\n
    queue_id --> Foregin key, pointing to the queue that the calendar is in.\n
    @author Yixuanzhou
    """
    __tablename__ = 'QueueCalendar'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    url = db.Column(db.String(255), nullable=False)
    color = db.Column(db.String(255), nullable=False)
    is_enabled = db.Column(db.Boolean, nullable=False, default=True)
    queue_id = db.Column(db.Integer, db.ForeignKey('queue.id'),
                         nullable=False)

    def __init__(self, **kwargs):
        """
        The constructor of the queue calendar object.\n
        Inputs:\n
        url --> The url of the calendar.\n
        color --> The color of the calendar.\n
        is_enablde --> Whether to enable to calendar or not (Default False).\n
        queue_id --> The queue_id that this calendar is in.\n
        """
        super(QueueCalendar, self).__init__(**kwargs)

    def save(self):
        """
        Save the object in the database.
        """
        db.session.commit()

    def to_json(self) -> Dict[QueueCalendar]:
        """
        Return the dictionary format for the current object.
        """
        ret = {}
        ret['id'] = self.id
        ret['url'] = self.url
        ret['color'] = self.color
        ret['is_enabled'] = self.is_enabled
        ret['queue_id'] = self.queue_id

    def delete_queue_calendar(self):
        """
        Delete the queue calendar.
        """
        self.is_enabled = False
        self.save()

    def enable_queue_calendar(self):
        """
        Enable the queue calendar.
        """
        self.is_enabled = True
        self.save()

    # Static query method
    @staticmethod
    def find_all_calendar_for_queue(queue_id: int) -> List[QueueCalendar]:
        """
        Find the all the queue calendars associsted to the queue.\n
        Inputs:\n
        queue --> The Queue to look for.\n
        Return:\n
        A list of queue calendar assocaited to the queue.\n
        """
        calendar_list = QueueCalendar.query().filter_by(queue_id=queue_id)
        return calendar_list
