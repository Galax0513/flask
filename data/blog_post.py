from datetime import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Posts(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    content = sqlalchemy.Column(sqlalchemy.Text)
    date_posted = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)
    slug = sqlalchemy.Column(sqlalchemy.String(200))
    img = sqlalchemy.Column(sqlalchemy.String(300))
    # Foreign Key To Link Users
    poster_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))


