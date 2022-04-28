import datetime
import sqlalchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from data.Sql.db_session import SqlAlchemyBase
from flask_login import UserMixin


class Subs(SqlAlchemyBase, UserMixin):
    __tablename__ = 'subscribers'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    subscriber = sqlalchemy.Column(sqlalchemy.Integer)
