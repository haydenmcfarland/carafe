from flask import Blueprint, request, jsonify, json
from carafe.database.model import Board, Post, Comment, User
from carafe import constants


def _dict_gen(**kwargs):
    filtered_dict = dict()
    for k in kwargs:
        if kwargs[k]:
            filtered_dict[k] = kwargs[k]
    return filtered_dict

api = Blueprint('api', __name__)


@api.route('/api/boards', methods=['GET'])
def api_boards():
    boards = Board.query.filter_by(deleted=False)
    return jsonify(boards=[_dict_gen(bid=b.bid, desc=b.desc, name=b.name) for b in boards])


@api.route('/api/board/<bid>/posts/', methods=['GET'])
def api_posts_by_bid(bid):
    post_range = request.args.get('post_range')
    start, end = 0, constants.RESOURCE_LIMIT
    message = ''
    if post_range:
        try:
            post_range = json.loads(post_range)
            if post_range[-1] - post_range[0] <= constants.RESOURCE_LIMIT:
                start, end = post_range[0], post_range[-1]
        except:
            message = "Invalid post_range parameter."
    posts = Post.query.filter_by(bid=bid, deleted=False)
    posts = sorted(posts, key=lambda x : x.recent_date())
    return jsonify(posts=[_dict_gen(pid=p.pid, user=p.get_username(), name=p.name, text=p.text) for p in posts])
