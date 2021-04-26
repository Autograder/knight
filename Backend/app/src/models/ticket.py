from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict
from operator import attrgetter

from ..utils.time import TimeUtil

from ...setup import db
from .user import User
from .enrolled_course import Role
from .course import Course
from .ticket_feedback import TicketFeedback
from .events.ticket_event import TicketEvent
from .enrolled_course import EnrolledCourse

"""
Note for implementation:
For all the queries methods in Ticket.java when it related to queue\
I will implement it in the queue.py instead of here.\n
"""

# Only 3 tags allowed per ticket
MAX_TAG_NUM = 3
# IF the room is not in cse building, the front end should pass in NON_CSE
NON_CSE = 'NON_CSE'
# IF the room is not in cse building, the front end should pass in HALLWAY
HALLWAY = 'HALLWAY'


class Status(Enum):
    """
    The status of the ticket with the following options --> database value:\n
    PENDING --> 0\n
    ACCEPTED --> 1\n
    RESOLVED --> 2\n
    CANCELED --> 3\n
    @author YixuanZhou
    """
    PENDING = 0
    ACCEPTED = 1
    RESOLVED = 2
    CANCELED = 3


class HelpType (Enum):
    """
    The type of the help the student need for this ticket\
        with the following options --> database value:\n
    Question --> 0\n
    Checkoff --> 1\n
    @author YixuanZhou
    """
    QUESTION = 0
    CHECKOFF = 1


class TicketTag (Enum):
    """
    All the types of the tags of a ticket ticket the \
        following options --> database value:
    GETTING_STARTED --> 0\n
    SPECIFICATION --> 1\n
    ALGORITHM --> 2\n
    PROGRAMING_LANGUAGE --> 3\n
    IMPLEMENTATION --> 4\n
    COMPILE_ERROR --> 5\n
    RUNTIME_ERROR --> 6\n
    WRONG_OUTPUT --> 7\n
    INFINITE_LOOP --> 8\n
    WEIRD_BEHAVIOR --> 9\n
    WEIRD_DEBUG --> 10\n
    @author YixuanZhou
    """
    GETTING_STARTED = 0
    SPECIFICATION = 1
    ALGORITHM = 2
    PROGRAMING_LANGUAGE = 3
    IMPLEMENTATION = 4
    COMPILE_ERROR = 5
    RUNTIME_ERROR = 6
    WRONG_OUTPUT = 7
    INFINITE_LOOP = 8
    WEIRD_BEHAVIOR = 9
    WEIRD_DEBUG = 10


class Ticket(db.Model):
    """
    The ticket model of the database.
    Fields:
    id --> The id of the ticket, unique primary key.\n
    created_at --> The time that this ticket is created,
                   default is the current time.\n
    closed_at --> The time that this ticket is closed. Nullable\n
    room --> The room that this student is in.\n
    workstation --> The workstation of the student.\n
    status --> The status of this ticket.\n
    title --> The title of this ticket.\n
    description --> The discription of the ticket created by student.\n
    ec_grader_id --> The EC grader_id who accepted this ticket, Nullable.\n
    queue_id --> The queue_id of which this ticket belongs to.\n
    ec_student_id --> The EC student_id who created this ticket.\n
    is_private --> Whether this ticket is private.\n
    accepted_at --> The time that this ticket was accepted.\n
    help_type --> The type of help student need.\n
    tag_one --> The ticket tag for this ticket. Not nullable since at least\
                a tag.\n
    tag_two --> The ticket tag for this ticket. Nullable.\n
    tag_three --> The ticket tag for this ticket. Nullable.\n
    @author YixuanZhou
    @author nouryehia (updates)
    """
    __tablename__ = 'Ticket'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=True,
                           default=TimeUtil.get_current_time())
    closed_at = db.Column(db.DateTime, nullable=True, default=None)
    room = db.Column(db.String(255), nullable=False)
    workstation = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, nullable=False,
                       default=Status.PENDING.value)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ec_grader_id = db.Column(db.Integer, db.ForeignKey('EnrolledCourse.id'),
                             nullable=True, default=None)
    queue_id = db.Column(db.Integer, db.ForeignKey('Queue.id'),
                         nullable=False)
    ec_student_id = db.Column(db.Integer, db.ForeignKey('EnrolledCourse.id'),
                              nullable=False)
    is_private = db.Column(db.Boolean, nullable=False)
    accepted_at = db.Column(db.DateTime, nullable=True, default=None)
    help_type = db.Column(db.Integer, nullable=False)
    tag_one = db.Column(db.Integer, nullable=False)
    tag_two = db.Column(db.Integer, nullable=True, default=None)
    tag_three = db.Column(db.Integer, nullable=True, default=None)

    def __init__(self, **kwargs):
        """
        The constructor of the ticket object.\n
        Inputs:\n
        created_at --> The time that ticket is created, default is None.\n
        room --> The room that this ticket is in.\n
        workstation --> the workstation that the ticket at.\n
        title --> The title of this ticket.\n
        description --> The description of this ticket.\n
        queue_id --> The queue it for that queue.\n
        ec_student_id --> The EC id of the student who created the ticket.\n
        is_private --> Wheather this ticket is private.\n
        helpy_type --> The type of help student demands.\n
        tag_one --> The first tag to the ticket.\n
        tag_two --> The second tag (default is none) to the ticket.\n
        tag_three --> The third tag (dfault is none) to the ticket.\n
        """
        super(Ticket, self).__init__(**kwargs)

    def save(self):
        """
        Save the changes made to the object into the database.\n
        """
        db.session.commit()

    def to_json(self, user_id=int) -> Dict[str, str]:
        '''
        Function that takes a ticket object and returns it in dictionary.
        We will hid the informations for those who do not have permission.\n
        Params: user_id --> The user for requesting this view\n
        Returns: Dictionary of the user info
        '''
        result = {}
        ret = {}
        evts = {}
        if self.can_view_by(user_id=user_id):
            ret['ticket_id'] = self.id
            ret['queue_id'] = self.queue_id
            ret['closed_at'] = self.closed_at
            ret['created_at'] = self.created_at
            ret['status'] = self.status
            ret['room'] = self.room
            ret['workstation'] = self.workstation
            ret['title'] = self.title
            ret['description'] = self.description
            ret['ec_grader_id'] = self.ec_grader_id
            ret['ec_student_id'] = self.ec_student_id
            ret['is_private'] = self.is_private
            ret['accepted_at'] = self.accepted_at
            ret['help_type'] = self.help_type
            ret['tag_one'] = self.tag_one
            ret['tag_two'] = self.tag_two
            ret['tag_three'] = self.tag_three
            cid = Course.get_course_by_queue_id(self.queue_id).id
            evts = TicketEvent.get_events_for_tickets(ticket_id=self.id,
                                                      course_id=cid,
                                                      user_id=user_id)
        else:
            ret['is_private'] = self.is_private

        result['ticket_info'] = ret
        result['ticket_events'] = evts
        return result

    # All the getter methods / status checking methods:
    def is_question(self) -> bool:
        """
        Return if the ticket is a question or not.\n
        Return:\n
        A bool value determing if it is a question.\n
        """
        return self.help_type == HelpType.QUESTION.value

    def is_checkoff(self) -> bool:
        """
        Return if the ticket is a checkoff or not.\n
        Return:\n
        A bool value determing if it is a checkoff.\n
        """
        return self.help_type == HelpType.CHECKOFF.value

    def is_pending(self) -> bool:
        """
        Return if the ticket is pending or not.\n
        Return:\n
        A bool value determing if it is pending.\n
        """
        return self.status == Status.PENDING.value

    def is_accepted(self) -> bool:
        """
        Return if the ticket is accepted or not.\n
        Return:\n
        A bool value determing if it is accepted.\n
        """
        return self.status == Status.ACCEPTED.value

    def is_resolved(self) -> bool:
        """
        Return if the ticket is resolved or not.\n
        Return:\n
        A bool value determing if it is resolved.\n
        """
        return self.status == Status.RESOLVED.value

    def is_canceled(self) -> bool:
        """
        Return if the ticket is canceled or not.\n
        Return:\n
        A bool value determing if it is canceled.\n
        """
        return self.status == Status.CANCELED.value

    def is_non_cse(self) -> bool:
        """
        Return if the ticket is not in CSE building or not.\n
        Return:\n
        A bool value determing if it is in CSE.\n
        """
        return self.room == NON_CSE.value

    def is_hallway(self) -> bool:
        """
        Return if the ticket is located at hallway.\n
        Return:\n
        A bool value determing if it is in the hallway.\n
        """
        return self.room == HALLWAY.value

    def get_tags_list(self) -> List[TicketTag]:
        """
        Return if the list of the tags that is on this ticket.\n
        Return:\n
        An array of size 1 to 3 with ticket tags in it.\n
        """
        ticket_tag = []
        ticket_tag.append(self.tag_one)
        if not self.tag_two:
            ticket_tag.append(self.tag_two)
        if self.tag_three is not None:
            ticket_tag.append(self.tag_three)
        return ticket_tag

    def get_help_time_in_second(self) -> float:
        """
        Get the time in second of the time that this ticket spent\
        to be resolved.\n
        Return:\n
        The difference in time.\n
        """
        return (self.closed_at - self.created_at).total_second()

    def get_title(self) -> str:
        """
        Return the title of the ticket.\n
        Return:\n
        The title in string.\n
        """
        return self.title

    def get_description(self) -> str:
        """
        Return the description of the ticket.\n
        Return:\n
        The description in string.\n
        """
        return self.description

    def get_room(self) -> str:
        """
        Return the room of the ticket.\n
        Return:\n
        The room in string.\n
        """
        return self.room

    def get_workstation(self) -> str:
        """
        Return the workstation of the ticket.\n
        Return:\n
        The workstation in string.\n
        """
        return self.room

    def get_position(self) -> int:
        """
        Return the position of the ticket in the current queue.\n
        Return:\n
        The position of the ticket (start from 1).\n
        """
        all_pending_tickets = Ticket.query.filter_by(
                                queue_id=self.queue_id,
                                status=Status.PENDING
                                ).all()
        all_pending_tickets.sort(key=attrgetter('created_at'))
        return all_pending_tickets.index(self) + 1

    # Get addition info outside the class
    def has_feedback(self) -> bool:
        """
        Check if this ticket has feedback.\n
        Return:\n
        Bool of saying if the ticket has a feedback or not.\n
        """
        return not self.get_latest_feedback()

    def get_latest_feedback(self) -> Optional[TicketFeedback]:
        """
        Get the latest feedback of this ticket.\n
        Return:\n
        The latest TicketFeedback Object.\n
        """
        return TicketFeedback.query.filter_by(
                ticket_id=self.ticket_id).order_by(
                TicketFeedback.submitted_date).first()

    def get_ticket_events(self) -> List[TicketEvent]:
        """
        Get the events that are happened on this ticket.
        Return:\n
        A list of the events happend on this ticket.
        """
        return TicketEvent.query.filter_by(
                ticket_id=self.id).order_by(id).all()

    # Permission of the ticket that a user has
    def can_view_by(self, user_id: int) -> bool:
        """
        Determine if the ticket can be viewed by a given user.\n
        Inputs:\n
        queue_id --> The queue the ticket beylongs to.\n
        user --> The User object of the user who is trying to view the
        ticket.\n
        Return:\n
        The bool for whether a user can view.\n
        """
        if not self.is_private:
            return True

        course = Course.get_course_by_queue_id(self.queue_id)
        ec_entry = EnrolledCourse.find_user_in_course(user_id=user_id,
                                                      course_id=course.id)
        if not ec_entry:
            return False

        if ec_entry.role != Role.STUDENT.value:
            return True

        return self.ec_student_id == ec_entry.id

    def can_edit_by(self, user_id: int) -> bool:
        """
        Determine if the ticket can be edited by a given user.\n
        Inputs:\n
        user --> The User object of the user who is trying to edit the
        ticket.\n
        Return:\n
        The bool for whether a user can edit.\n
        """
        if self.is_resolved():
            return False

        course = Course.get_course_by_queue_id(self.queue_id)
        ec_entry = EnrolledCourse.find_user_in_course(user_id=user_id,
                                                      course_id=course.id)

        if not ec_entry:
            return False

        if ec_entry.role != Role.STUDENT.value:
            return True

        return self.ec_student_id == ec_entry.id

    def update_ticket_tags(self, tag_list: List[TicketTag]) -> None:
        """
        Update the tags on the ticket.\n
        Input:\n
        tag_list --> The list of tags in which everything is of the type\
                     TicketTag.\n
        """
        # Update the tags
        self_tag_list = []
        for i in range(0, MAX_TAG_NUM):
            if i < len(tag_list):
                self_tag_list.append(tag_list[i])
            else:
                self_tag_list.append(None)

        # Assign the instance tags from the list
        self.tag_one = self_tag_list[0]
        self.tag_two = self_tag_list[1]
        self.tag_three = self_tag_list[2]

        # Update the database
        self.save()

    # Setter functions
    def mark_pending(self) -> None:
        """
        Mark the ticket as pending status.\n
        """
        self.status = Status.PENDING.value
        self.ec_grader_id = None
        self.save()

    def mark_accepted_by(self, grader: User) -> None:
        """
        Mark the ticket as accepted by a tutor.\n
        """
        # Prevent a tutor accept multiple tickets
        Ticket.defer_accepted_ticket_for_grader(grader, self.queue_id)

        self.status = Status.ACCEPTED.value
        self.accepted_at = TimeUtil.get_current_time()
        self.ec_grader_id = EnrolledCourse.find_user_in_course(
                            user_id=grader.id,
                            course_id=Course.get_course_by_queue_id(
                                self.queue_id).id).id

        self.save()

    def mark_resolved(self) -> None:
        """
        Mark the ticket as resolved.\n
        """
        self.status = Status.RESOLVED.value
        self.closed_at = TimeUtil.get_current_time()
        self.save()

    def mark_canceled(self) -> None:
        """
        Mark the ticket as canceled.\n
        """
        self.status = Status.CANCELED.value
        self.closed_at = TimeUtil.get_current_time()
        self.save()

    def student_update(self, title: str, description: str, room: str,
                       workstation: str, is_private: bool, help_type: HelpType,
                       tag_list: List[TicketTag]) -> None:
        """
        This method updates the current ticket. By taking in the updates from
        front end, this will update the corresponding tickit in the database.
        Inputs:
        title --> The title of the ticket.\n
        description --> The description of the ticket.\n
        room --> The room that the student is in.\n
        workstation --> The workstation of the student.\n
        ipPrivate --> Whether the student want this ticket to be private.\n
        help_type --> The type of help the student demends.\n
        """
        # Perform update for all the basic info
        self.title = title
        self.description = description
        self.room = room
        self.workstation = workstation
        self.is_private = is_private
        self.help_type = help_type.value

        # Commit the updates for basica info
        self.save()

        # Update ticket tags
        self.update_ticket_tags(tag_list)

        return True

    # Note:
    # So far not implementing the methods used by controllers, including
    # findOldestForQueue
    # findNewestForQueue
    # findOldestForQueueForGrader
    # findNewestForQueueForGrader
    # findNewestForStudent
    # For NewsFeedPost including:
    # findResolvedTicketsForQueueForGraderAfter
    # findLastResolvedTicketForQueueForGrader
    # For TicketFeedback:
    # findNewestFeedback should be in TicketFeedback

    # Static add method
    @staticmethod
    def add_ticket(queue_id: int, student_id: int, title: str,
                   description: str, room: str,
                   workstation: str, is_private: bool,
                   help_type: HelpType,
                   tag_list: List[TicketTag]) -> Ticket:
        """
        Add a ticket.\n
        Inputs:\n
        student --> The student who submit the ticket.\n
        title --> The title of the ticket.\n
        description --> The description to the ticket.\n
        room --> The room of this ticket is in.\n
        workstation --> The workstaton ticket is at.\n
        help_type --> The type of help needed.\n
        tag_list --> The list of tags of the tickte.\n
        Return:\n
        The created ticket.\n
        @author: Yixuan
        """
        tag_one = tag_list[0]
        tag_two = tag_list[1] if len(tag_list) > 1 else None
        tag_three = tag_list[2] if len(tag_list) > 2 else None

        cid = Course.get_course_by_queue_id(queue_id).id
        ec = EnrolledCourse.find_user_in_course(user_id=student_id,
                                                course_id=cid).id

        new_ticket = Ticket(created_at=TimeUtil.get_current_time(),
                            closed_at=None,
                            room=room, workstation=workstation,
                            title=title, description=description,
                            ec_grader_id=None, queue_id=queue_id,
                            ec_student_id=ec, is_private=is_private,
                            accepted_at=None, help_type=help_type.value,
                            tag_one=tag_one, tag_two=tag_two,
                            tag_three=tag_three, status=Status.PENDING.value)
        Ticket.add_to_db(new_ticket)
        return new_ticket

    @staticmethod
    def add_to_db(ticket: Ticket):
        """
        Add the ticket to the database.\n
        Inputs:\n
        ticket --> the ticket object created.\n
        """
        db.session.add(ticket)
        db.session.commit()

    @staticmethod
    def get_ticket_by_id(ticket_id: int) -> Optional[Ticket]:
        """
        Get the ticket by ticket_id.\n
        Inputs:\n
        ticket_id --> The ticket_id to look for.\n
        Return:\n
        The ticket object, None if the ticket_id is not found.\n
        """
        return Ticket.query.filter_by(id=ticket_id).first()

    # Ticket stats calultaions
    @staticmethod
    def find_ticket_accepted_by_grader(grader_id: int, queue_id: int) ->\
            Optional[Ticket]:
        """
        Find the last ticket accepted by the grader.\n
        There should only be one ticket that is accpeted by the grader.\n
        Inputs:\n
        grader --> The User object of the grader to look up.\n
        Return:\n
        The ticket that was accepted by the grader.\n
        """
        cid = Course.get_course_by_queue_id(queue_id).id
        ec = EnrolledCourse.find_user_in_course(user_id=int(grader_id),
                                                course_id=cid).id

        return Ticket.query.filter_by(status=Status.ACCEPTED,
                                      ec_grader_id=ec).first()

    # Ticket stats calultaions
    @staticmethod
    def average_resolved_time(resolved_tickets: List[Ticket]) -> int:
        """
        Given a list of tickest, get the average time in second for resolve
        time.\n
        Inputs:\n
        resolved_tickets --> a list of tickests that has been resolved.\n
        Return:\n
        The number of the average time in seconds.\n
        """
        sum_time = 0
        for ticket in resolved_tickets:
            sum_time += ticket.get_help_time_in_second()
        return sum_time // len(resolved_tickets)

    @staticmethod
    def defer_accepted_ticket_for_grader(grader: User, queue_id: int) -> int:
        """
        Set all the accepted ticket for a grader to pending incase multiple
        tickets is accepted by one grader.\n
        Inputs:\n
        grader --> The grader to be multified.\n
        """
        cid = Course.get_course_by_queue_id(queue_id).id
        ec = EnrolledCourse.find_user_in_course(user_id=grader.id,
                                                course_id=cid).id

        ticket_list = Ticket.query.filter_by(ec_grader_id=ec).all()
        counter = 0

        for ticket in ticket_list:
            if (ticket.status == Status.ACCEPTED.value):
                counter += 1
                ticket.mark_pending()

        return counter

    # Moved from ticket_event

    # static query methods
    @staticmethod
    def find_all_events_for_ticket(ticket: Ticket) -> List[TicketEvent]:
        """
        Find all the ticket events associated to a ticket.\n
        Inputs:\n
        ticket --> The ticket object to be look for.\n
        Return:\n
        A list of event related to this ticket.\n
        """
        return TicketEvent.query().filter_by(ticket_id=ticket.id)\
            .order_by(TicketEvent.timestamp.desc()).all()

    @staticmethod
    def find_all_events_for_tickets(tickets:
                                    List[Ticket]) -> List[TicketEvent]:
        """
        Find all the ticket events of multiple tickets.\n
        Inputs:\n
        tickets --> A list of ticktes.\n
        Return:\n
        A list of event related to the tickets passed in.\n
        """
        return TicketEvent.query().\
            filter_by(Ticket.ticket_id.in_(tickets))

    # Moved from ticket_feedback

    # Static query methods for ticket feedbacks
    @staticmethod
    def get_ticket_feedback(ticket_list: List[Ticket]) -> List[TicketFeedback]:
        """
        Given a list of tickets, get the feedback of each ticket and put
        them into a list.\n
        Inputs:\n
        ticket_list --> The list of tickets to look for.\n
        Returns:\n
        A list of TicketFeedback, if a ticket does not have a feedback,
        it will not show up in the list.\n
        """
        feedback_list = []
        for ticket in ticket_list:
            feedback = TicketFeedback.query().filter_by(ticket_id=ticket.id)\
                        .ordered_by(TicketFeedback.submitted_date).first()
            if feedback is not None:
                feedback_list.append(feedback)
        return feedback_list

    @staticmethod
    def find_all_tickets(queue_id: int,
                         status: List[Status] = [Status.PENDING,
                                                 Status.ACCEPTED])\
            -> List[Ticket]:
        """
        Get a list of all the tickets for a queue with decending order
        by the time it was created.\n
        Input:\n
        queue --> The queue to search for.\n
        status --> Optional params for finding tickets with specific list
        status.\n
        Return:\n
        The list of the ticket of this queue ordered by create time.\n
        """
        if status:
            return Ticket.\
                query.filter_by(queue_id=queue_id).\
                filter(Ticket.status.in_(status)).\
                order_by(Ticket.created_at.desc()).all()
        else:
            return Ticket.query.\
                filter_by(queue_id=queue_id).\
                order_by(Ticket.created_at.desc()).all()

    @staticmethod
    def find_all_tickets_by_student(queue_id: int,
                                    student_id: int,
                                    status: List[Status]) -> List[Ticket]:
        """
        Get a list of all the tickets for a queue created by a student
        with decending order by the time it was created.\n
        Input:\n
        queue --> The queue to search for.\n
        student --> The student to be looked for.\n
        status --> The list of status to filter.\n
        Return:\n
        The list of the ticket of this queue ordered by create time.\n
        """
        cid = Course.get_course_by_queue_id(queue_id).id
        ec = EnrolledCourse.find_user_in_course(user_id=student_id,
                                                course_id=cid).id
        return (Ticket.query.
                filter_by(queue_id=queue_id, ec_student_id=ec).
                filter(Ticket.status.in_(status)).
                order_by(Ticket.created_at.desc()).all() if status else
                Ticket.query.
                filter_by(queue_id=queue_id, ec_student_id=ec).
                order_by(Ticket.created_at.desc()).all())

    @staticmethod
    def find_all_tickets_for_grader(queue_id: int,
                                    grader_id: int) -> List[Ticket]:
        """
        Get a list of all the tickets for a queue handled by a grader
        with decending order by the time it was created.\n
        Input:\n
        queue --> The queue to search for.\n
        grader --> The grader to be looked for.\n
        Return:\n
        The list of the ticket of this queue ordered by create time.\n
        """
        cid = Course.get_course_by_queue_id(queue_id).id
        ec = EnrolledCourse.find_user_in_course(user_id=grader_id,
                                                course_id=cid).id
        return Ticket.query.\
            filter_by(queue_id=queue_id, ec_grader_id=ec).\
            order_by(Ticket.created_at.desc()).all()

    @staticmethod
    def find_tickets_in_range(queue_id: int,
                              start: str,
                              end: str,
                              grader_id: int = None,
                              resolved: bool = False):
        """
        Find all the ticktes of the queue in range of two datetimes. Can be
        categrized as resolved if wanted and grader_id can be specified\n
        Input:\n
        queue_id --> The id of the queue to look at.\n
        grader --> An optional User object, use it if want to find for a
                   grader.\n
        reolved --> An optional boolean, indicating whether we only want
                    resolved tickets or not.
        start --> The begining of the range,
                it would be 1 hour before by default.\n
        end --> The end of the range, it would be now by default.\n
        Return:\n
        A list of tickets in this range.\n
        """
        if resolved:
            if not grader_id:
                tl = Ticket.query.filter_by(queue_id=queue_id,
                                            status=Status.RESOLVED.value).all()
            else:
                cid = Course.get_course_by_queue_id(queue_id).id
                ec = EnrolledCourse.find_user_in_course(user_id=grader_id,
                                                        course_id=cid).id
                tl = Ticket.query.filter_by(queue_id=queue_id,
                                            ec_grader_id=ec,
                                            status=Status.RESOLVED.value).all()
        else:
            if not grader_id:
                tl = Ticket.query.filter_by(queue_id=queue_id).all()
            else:
                cid = Course.get_course_by_queue_id(queue_id).id
                ec = EnrolledCourse.find_user_in_course(user_id=grader_id,
                                                        course_id=cid).id
                tl = Ticket.query.filter_by(queue_id=queue_id,
                                            ec_grader_id=ec).all()

        start = (TimeUtil.convert_str_to_datetime(
                 TimeUtil.get_time_before(hours=1)) if not start else
                 TimeUtil.convert_str_to_datetime(start))

        end = (TimeUtil.convert_str_to_datetime(
               TimeUtil.get_current_time()) if not end else
               TimeUtil.convert_str_to_datetime(end))

        return list(filter(lambda x: start <=
                           TimeUtil.naive_to_aware(x.created_at) <= end, tl))

    @staticmethod
    def find_ticket_history_with_offset(queue_id: int, offset: int = 0,
                                        limit: int = 10,
                                        student: User = None,
                                        grader: User = None) -> List[Ticket]:
        """
        Find a list of tickets with certain offsets and limits with the order
        of ticket_id.\n
        Inputs:\n
        queue --> The queue to look up.\n
        offset --> The offset to start looking up.\n
        limit --> The limit of to display.\n
        Return:\n
        A list of tickets.
        """
        cid = Course.get_course_by_queue_id(queue_id)
        if student:
            sid = EnrolledCourse.find_user_in_course(user_id=student.id,
                                                     course_id=cid).id
            return Ticket.query.filter_by(queue_id=queue_id).\
                filter_by(Ticket.status.in_(Status.RESOLVED,
                                            Status.CANCELED)).\
                filter_by(ec_student_id=sid).\
                sort_by(id).offset(offset).limit(limit).all()
        elif grader is not None:
            gid = EnrolledCourse.find_user_in_course(grader_id=grader.id,
                                                     course_id=cid).id
            return Ticket.query.filter_by(queue_id=queue_id).\
                filter_by(Ticket.status.in_(Status.RESOLVED,
                                            Status.CANCELED)).\
                filter_by(ec_grader_id=gid).\
                sort_by(id).offset(offset).limit(limit).all()
        else:
            Ticket.query.filter_by(queue_id=queue_id).\
                filter_by(Ticket.status.in_(Status.RESOLVED,
                                            Status.CANCELED)).\
                sort_by(id).offset(offset).limit(limit).all()

    @staticmethod
    def find_all_feedback_for_queue(queue_id: int) -> List[TicketFeedback]:
        """
        Find all the feedbacks for a queue given a queue_id
        Note: This function should only be called from queue.
        Inputs:\n
        queue_id --> int
        Returns:\n
        A list of ticket feedback
        """
        tickets = Ticket.find_all_tickets(queue_id, [Status.RESOLVED])
        feedbacks = []
        for t in tickets:
            feedbacks += (TicketFeedback.get_ticket_feedback(t))
        return feedbacks

    @staticmethod
    def find_feedback_for_grader(queue_id: int,
                                 grader_id: int) -> List[TicketFeedback]:
        """
        Find all the feedback to a grader that is in the queue.
        Note: This function should only be called from queue.
        Inputs:\n
        queue --> The Queue object to search for.\n
        grader --> The User object for the grader to search for.\n
        Return:\n
        A list of ticket feedbacks to the grader.\n
        """
        tickets = Ticket.find_all_tickets_for_grader(queue_id, grader_id)
        feedbacks = []
        for t in tickets:
            fb = TicketFeedback.get_ticket_feedback(ticket_id=t.id)
            fb['name'] = 'anonymous'
            if not fb['is_anonymous']:
                user_id = EnrolledCourse.get_ec_by_id(t.ec_student_id).user_id
                user = User.get_user_by_id(user_id)
                fb['name'] = user.first_name + ' ' + user.last_name
            feedbacks.append(fb)
        return feedbacks

    @staticmethod
    def find_feedback_for_student(queue_id: int,
                                  student_id: int) -> List[TicketFeedback]:
        """
        Find all the feedback from a student that is in the queue.
        Note: This function should only be called from queue.
        Inputs:\n
        queue --> The Queue object to search for.\n
        student --> The User object for the student to search for.\n
        Return:\n
        A list of ticket feedbacks from the student.\n
        """
        tickets = Ticket.find_all_tickets_for_student(queue_id, student_id)
        feedbacks = []
        for t in tickets:
            feedbacks.append(TicketFeedback.get_ticket_feedback(t))
        return feedbacks
