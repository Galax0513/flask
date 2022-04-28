import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import relationship

from data.Sql.db_session import SqlAlchemyBase


class Comments(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, unique=True)
    user_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.id"))
    post_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("posts.id"))
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    likes = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    post = relationship('Posts', backref="comments", lazy=True)
    user = relationship('User', backref="comments", lazy=True)
