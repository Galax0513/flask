import datetime
import sqlalchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from data.db_session import SqlAlchemyBase
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    game_stat = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    # User can Have Many Posts
    posts = relationship("Posts", backref="poster")  # poster.name

    def repr(self):
        return f"{self.name} {self.surname}"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


'''from datetime import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    nickname = sqlalchemy.Column(sqlalchemy.String(), nullable=False, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String(120), nullable=False, unique=True)
    favorite_color = sqlalchemy.Column(sqlalchemy.String(120))
    date_added = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)
    password_hash = sqlalchemy.Column(sqlalchemy.String(120))

    @property
    def password(self):
        raise AttributeError("password id not a readable attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return f'<User>{self.id} {self.name} {self.email}'''

