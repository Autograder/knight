from datetime import datetime

from ..models.ticket import Ticket
from ..models.queue import Queue
from ..models.user import User
from ..models.events.queue_login_event import QueueLoginEvent
from ..models.events.ticket_event import TicketEvent
from .time import TimeUtil


class TutoringSession:
    """
    Holds information about tutor sessions for stats.
    Fields:
    start --> start time of session
    end --> end time of session
    duration --> duration of session
    time_helping --> time grader spent resolving tickets during session
    utlization --> time_helping / duration
    accepted --> number of tickets accepted during session
    resolved --> number of tickets resolved during session
    """
    def __init__(self, start, end, duration, time_helping, utilization,
                 accepted, resolved):
        self.start = start
        self.end = end
        self.duration = duration
        self.time_helping = time_helping
        self.utilization = utilization
        self.accepted = accepted
        self.resolved = resolved


def get_total_time_on_duty(qle: QueueLoginEvent, queue: Queue, grader: User,
                           start_date: TimeUtil = None):
    """
    Gets the total time spent on duty for a grader within a given time frame.
    Inputs:
    qle --> QueueLoginEvent object used to access the database
    queue --> queue on which the grader worked
    grader --> grader bing queried
    start_date --> (optional) start time of week being queried
    Return:
    Total time (in seconds) spent on duty by grader during the week that starts
    at start_date (if it was passed in) or during the whole quarter (if it was
    not).
    """
    if start_date is None:
        events = qle.find_event_in_range(queue, TimeUtil.min_time(),
                                         TimeUtil.get_current_time(), grader)
    else:
        end_date = (start_date.convert_str_to_datetime()
                    + datetime.timedelta(days=7)).isoformat()
        events = qle.find_event_in_range(queue, start_date, end_date, grader)

    total_time_on_duty = 0

    for i in range(0, len(events), 2):
        start = events[i].timestamp
        end = (TimeUtil.get_current_time.now() if i == len(events) - 1
               else events[i + 1].timestamp)

        time_on_duty = end - start
        total_time_on_duty += time_on_duty.seconds

    return total_time_on_duty


def get_num_tickets_handled(queue: Queue, grader: User,
                            start_date: datetime = None):
    """
    Gets the number of tickets handled by a grader within a given time frame.
    Inputs:
    queue --> queue on which the grader worked
    grader --> grader bing queried
    start_date --> (optional) start time of week being queried
    Return:
    Number of tickets handled by grader during the week that starts at
    start_date (if it was passed in) or during the whole quarter (if it was
    not).
    """
    if start_date is None:
        tickets = Ticket.find_all_tickets_in_range(queue, grader)
    else:
        end_date = (start_date.convert_str_to_datetime()
                    + datetime.timedelta(days=7)).isoformat()
        tickets = Ticket.find_tickets_in_range(queue, start_date, end_date,
                                               grader)

    return len(tickets)


def get_total_time_spent_resolving_tickets(queue: Queue, grader: User,
                                           start_date: datetime = None):
    """
    Gets the amount of time a tutor has spent resolving tickets within a given
    time frame.
    Inputs:
    queue --> queue on which the grader worked
    grader --> grader bing queried
    start_date --> (optional) start time of week being queried
    Return:
    Amount of time (in seconds) that grader spent resolving tickets during the
    week that starts at start_date (if it was passed in) or during the whole
    quarter (if it was not).
    """
    if start_date is None:
        tickets = Ticket.find_all_tickets_in_range(queue, grader)
    else:
        end_date = (start_date.convert_str_to_datetime()
                    + datetime.timedelta(days=7)).isoformat()
        tickets = Ticket.find_tickets_in_range(queue, start_date, end_date,
                                               grader)

    for ticket in tickets:
        events = TicketEvent.find_all_events_for_ticket(ticket)
        events = [event for event in events if event.user_id == grader.id]

        total_time = 0
        time_accepted = datetime.min()

        for e in events:
            if e.is_accepted():
                time_accepted = e.timestamp

            if (time_accepted != datetime.min and
               (e.is_resolved() or e.is_deferred() or e.is_canceled)):
                time_helping = e.timestamp - time_accepted
                total_time += time_helping.seconds
                time_accepted = datetime.min()

    return total_time


def get_average_time_spent_resolving_ticket(queue: Queue, grader: User,
                                            start_date: datetime = None):
    """
    Gets the average time a grader spent on each ticket within a given time
    frame.
    Inputs:
    queue --> queue on which the grader worked
    grader --> grader bing queried
    start_date --> (optional) start time of week being queried
    Returns:
    Average time (in seconds) grader spent on each ticket during the week that
    starts at start_date (if it was passed in) or during the whole quarter (if
    it was not).
    """
    return (get_total_time_spent_resolving_tickets(queue, grader, start_date) /
            get_num_tickets_handled(queue, grader, start_date))


def get_tutoring_sessions(qle: QueueLoginEvent, queue: Queue, grader: User,
                          start_date: datetime = None):
    """
    Gets all the tutoring sessions of a grader within a given time frame.
    Sessions include info about start/end time, duration, time helping,
    utilization rate, and number of tickets accepted/resolved.
    Inputs:
    qle --> QueueLoginEvent object used to access the database
    queue --> queue on which the grader worked
    grader --> grader bing queried
    start_date --> (optional) start time of week being queried
    Return:
    List of sessions
    """
    if start_date is None:
        events = qle.find_event_in_range(queue, datetime.min, datetime.now(),
                                         grader)
    else:
        end_date = (start_date.convert_str_to_datetime()
                    + datetime.timedelta(days=7)).isoformat()
        events = qle.find_event_in_range(queue, start_date, end_date, grader)

    sessions = []
    for i in range(0, len(events), 2):
        start = events[i].timestamp
        end = (datetime.now() if i == len(events) - 1
               else events[i + 1].timestamp)
        duration = end - start

        tickets = Ticket.find_tickets_in_range(queue, start, end, grader)

        time_accepted = datetime.min()
        total_time_helping = 0
        accepted = 0
        resolved = 0

        for ticket in tickets:
            for e in events:
                if e.is_accepted():
                    accepted += 1
                    time_accepted = e.timestamp

                if e.is_resolved():
                    resolved += 1

                if (time_accepted != datetime.min and
                   (e.is_resolved() or e.is_deferred() or e.is_canceled)):
                    time_helping = e.timestamp - time_accepted
                    total_time_helping += time_helping.seconds
                    time_accepted = datetime.min()

        utilization = time_helping / duration

    sessions.append(TutoringSession(start, end, duration, total_time_helping,
                                    utilization, accepted, resolved))

    return sessions
