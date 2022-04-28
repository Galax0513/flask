from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
import json

from data.Models.blog_post import Posts
from data.Models.users import User
from data.Models.stats import Stats
from data.Sql import db_session


class GetPos(Resource):
    def get(self):
        with open('pos.txt', mode='rt') as file:
            return jsonify(json.load(file))


class PostsResource(Resource):
    def get(self, post_id):
        db_sess = db_session.create_session()
        post = db_sess.query(Posts).get(post_id)
        return jsonify({"posts": post.to_dict()})


class PostsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        posts = db_sess.query(Posts)
        return jsonify({"posts": [post.to_dict() for post in posts]})


class UsersResource(Resource):
    def get(self, user_id):
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        return jsonify({"posts": user.to_dict()})


class UsersListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        users = db_sess.query(User)
        return jsonify({"posts": [user.to_dict() for user in users]})


class StatsResource(Resource):
    def get(self, stat_id):
        db_sess = db_session.create_session()
        stat = db_sess.query(Stats).get(stat_id)
        return jsonify({"posts": stat.to_dict()})


class StatsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        stats = db_sess.query(Stats)
        return jsonify({"posts": [stat.to_dict() for stat in stats]})


