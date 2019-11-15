""" Carafe REST API - WIP """

from flask import Blueprint, request, jsonify, json
from carafe.database.model import Board, Post
from carafe import constants

API = Blueprint('api', __name__)


@API.route('/api/boards', methods=['GET'])
def api_boards():
    """
    get all boards
    """
    boards = Board.query.filter_by(deleted=False)
    return jsonify(
        boards=[
            {
                "bid": b.bid,
                "desc": b.desc,
                "name": b.name
            } for b in boards])


@API.route('/api/board/<bid>/posts/', methods=['GET'])
def api_posts_by_bid(bid):
    """
    get all posts by board id
    """
    post_range = request.args.get('post_range')
    if post_range:
        post_range = json.loads(post_range)
        if post_range[-1] - post_range[0] <= constants.RESOURCE_LIMIT:
            pass
    posts = Post.query.filter_by(bid=bid, deleted=False)
    posts = sorted(posts, key=lambda x: x.recent_date())
    return jsonify(
        posts=[
            {
                "pid": p.pid,
                "user": p.get_username(),
                "name": p.name,
                "text": p.text
            } for p in posts])
