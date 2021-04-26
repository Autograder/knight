from flask_cors import CORS
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify

from ..models.ticket import Ticket
from ..models.ticket_feedback import TicketFeedback, Rating


feedback_api_bp = Blueprint('feedback_api', __name__)
CORS(feedback_api_bp, supports_credentials=True)


@feedback_api_bp.route('/add_feedback', methods=['POST'])
@login_required
def add_ticket_feedback():
    """
    Add ticket feedback related to a ticket by student.
    """
    ticket_id = int(request.json['ticket_id'])
    rating = Rating(request.json['rating'])
    feedback = request.json['feedback']
    is_anonymous = bool(request.json['is_anonymous']) if 'is_anonymous' \
        in request.json else True

    t = Ticket.get_ticket_by_id(ticket_id=ticket_id)
    if not t.is_resolved():
        return jsonify({'reason': 'Ticket has not been resolved'}), 400
    else:
        fb = TicketFeedback.add_feedback(ticket_id=ticket_id,
                                         rating=rating,
                                         feedback=feedback,
                                         anonymous=is_anonymous)
        return jsonify({'reason': 'feedback added',
                        'feedback': fb.to_json()}), 200


@feedback_api_bp.route('/get_feedback', methods=['GET'])
@login_required
def get_ticket_feedback():
    """
    Get ticket feedback from a ticket.
    """
    t_id = request.args.get('ticket_id', type=int)
    t = Ticket.get_ticket_by_id(t_id)
    if not t.can_view_by(current_user.id):
        return {'reason': 'permission denied', 'feedbacks': ""}, 200
    else:
        feedbacks = TicketFeedback.get_ticket_feedback(ticket_id=t_id)
        feedbacks = [feedback.to_json() for feedback in feedbacks]
        return {'reason': 'success', 'feedbacks': feedbacks}, 200
