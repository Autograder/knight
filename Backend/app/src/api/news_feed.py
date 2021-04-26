from flask_cors import CORS
from flask import Blueprint, request, jsonify
from flask_login import login_required


from ..models.news_feed_post import NewsFeedPost
from ..models.user import User

newsfeed_api_bp = Blueprint('newsfeed_api', __name__)
CORS(newsfeed_api_bp, supports_credentials=True)


@newsfeed_api_bp.route('/get_posts', methods=['GET'])
#@login_required
def get_news_feed_posts():

    '''
    Route used for retrieving news feed posts for a given queue
    @author allen
    '''
    req = request.json
    queue_id = req.get('queue_id')

    if not queue_id:
        return jsonify({'reason': 'invalid queue information'}), 400

    posts = NewsFeedPost.get_posts(queue_id)
    return_res = {'reason': 'success', 'result': posts}
    return return_res


@newsfeed_api_bp.route('/add_post', methods=['POST'])
#@login_required
def add_newsfeed_post():
    
    '''
    Route used to add a news feed post created by user for a specific
    queue
    @author allen
    '''
    req = request.json
    user_id = req.get('user_id')
    queue_id = req.get('queue_id')
    subject = req.get('subject')
    body = req.get('body')

    if not user_id or not queue_id or not subject or not body:
        return jsonify({'reason': 'invalid request'}), 400

    post = NewsFeedPost(subject=subject, body=body, 
                        owner_id=user_id, queue_id=queue_id)
    NewsFeedPost.add_to_db(post)
    
    return jsonify({'reason': 'news feed post created'}), 200


@newsfeed_api_bp.route('/update_post', methods=['POST'])
#@login_required
def update_newsfeed_post():

    '''
    Route is used to update a news feed post by the owner of the
    post for a given queue of a course
    @author allen
    '''
    req = request.json
    post_id = req.get('post_id')
    user_id = req.get('user_id')
    queue_id = req.get('queue_id')

    if not post_id or not user_id or not queue_id:
        return jsonify({'reason': 'invalid request'}), 400

    post = NewsFeedPost.get_post(queue_id, post_id)

    if not post or post.owner_id != user_id:
        return jsonify({'reason': 'invalid request'}), 400

    user = User.get_user_by_id(user_id)

    if not user:
        return jsonify({'reason': 'invalid request'}), 400

    subject = req.get('subject')
    body = req.get('body')

    post.edit(user, subject, body)

    return jsonify({'reason': 'news feed post updated'}), 200


@newsfeed_api_bp.route('/archive_post', methods=['POST'])
#@login_required
def archive_newsfeed_post():

    '''
    Route is used for archiving a specific news feed post for a given queue
    @author allen
    '''
    req = request.json
    post_id = req.get('post_id')
    queue_id = req.get('queue_id')

    if not post_id or not queue_id:
        return jsonify({'reason': 'invalid request'}), 400

    post = NewsFeedPost.get_post(queue_id, post_id)

    if not post:
        return jsonify({'reason': 'invalid request'}), 400

    post.archive()

    return jsonify({'reason': 'news feed post archived'}), 200


@newsfeed_api_bp.route('/unarchive_post', methods=['POST'])
#@login_required
def unarchive_newsfeed_post():

    '''
    Route is used for unarchiving a route that was archived before
    @author allen
    '''
    req = request.json
    post_id = req.get('post_id')
    queue_id = req.get('queue_id')

    if not post_id or not queue_id:
        return jsonify({'reason': 'invalid request'}), 400

    post = NewsFeedPost.get_post(queue_id, post_id)

    if not post:
        return jsonify({'reason': 'invalid request'}), 400

    post.unarchive()

    return jsonify({'reason': 'news feed post unarchived'}), 200


@newsfeed_api_bp.route('delete_post', methods=['POST'])
#@login_required
def delete_newsfeed_post():

    '''
    Route is used for deleting a post by simply archiving it when
    given a post id for a specific queue
    @author allen
    '''
    req = request.json
    post_id = req.get('post_id')
    queue_id = req.get('queue_id')

    if not post_id or not queue_id:
        return jsonify({'reason': 'invalid request'}), 400

    post = NewsFeedPost.get_post(queue_id, post_id)

    if not post:
        return jsonify({'reason': 'invalid request'}), 400

    post.archive()

    return jsonify({'reason': 'news feed post archived'}), 200