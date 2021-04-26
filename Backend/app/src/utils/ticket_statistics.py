from ..models.ticket import Ticket
from ..models.queue import Queue
from ..models.user import User
from ..models.ticket_feedback import TicketFeedback


def get_total_rating(queue: Queue):

    """
    Gets the total ratings submitted by students for a given queue.
    Inputs:
    queue --> queue on which the instructor is accessing the stats
    Return:
    dictionary of counts for good, neutral, and bad ratings
    """
    tickets = Ticket.find_all_tickets(queue, [2])
    stats = {0: 0, 1: 0, 2: 0}
    for ticket in tickets:
        feedback = TicketFeedback.get_ticket_feedback(ticket.id)
        if feedback is not None:
            rating = feedback[0].rating
            if rating is not None:
                stats[rating] = stats[rating] + 1

    normailzed_stats = {}
    normailzed_stats['good'] = stats[2]
    normailzed_stats['neutral'] = stats[1]
    normailzed_stats['bad'] = stats[0]

    return normailzed_stats


def get_ticket_counts_by_grader(queue: Queue):

    """
    Gets the count of tickets taken by each tutor for a given queue.
    Inputs:
    queue --> queue on which the instructor is accessing the stats
    Return:
    dictionary of counts of tickets resolved by each tutor for thes given queue
    """
    tickets = Ticket.find_all_tickets(queue, [2])
    stats = {}

    for ticket in tickets:
        grader_id = ticket.grader_id
        if grader_id is not None:
            grader = User.get_user_by_id(int(grader_id))
            if grader is not None:
                fname = grader.first_name
                lname = grader.last_name
                name = fname + ' ' + lname
                if name in stats:
                    stats[name] = stats[name] + 1
                else:
                    stats[name] = 1

    return stats


def get_ticket_counts_by_student(queue: Queue):

    """
    Gets the count of tickets created by each student for a given queue.
    Inputs:
    queue --> queue on which the instructor is accessing the stats
    Return:
    dictionary of counts of tickets created by each student for the given queue
    """
    tickets = Ticket.find_all_tickets(queue)
    stats = {}

    for ticket in tickets:
        student_id = ticket.student_id
        if student_id is not None:
            student = User.get_user_by_id(int(student_id))
            if student is not None:
                fname = student.first_name
                lname = student.last_name
                name = fname + ' ' + lname
                if name in stats:
                    stats[name] = stats[name] + 1
                else:
                    stats[name] = 1

    return stats
