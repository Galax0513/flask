from datetime import datetime
import sqlalchemy
from sqlalchemy.orm import relationship

from data.Sql.db_session import SqlAlchemyBase


class Posts(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    content = sqlalchemy.Column(sqlalchemy.Text)
    date_posted = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)
    slug = sqlalchemy.Column(sqlalchemy.String(200))
    files = sqlalchemy.Column(sqlalchemy.String())
    address = sqlalchemy.Column(sqlalchemy.String(200))
    coords = sqlalchemy.Column(sqlalchemy.String(100))
    place = sqlalchemy.Column(sqlalchemy.String())
    # Foreign Key To Link Users
    poster_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))

    def to_dict(self, only=("title", "content", "date_posted", "slug", "address")):
        data = {}
        for elem in only:
            data[elem] = self.__dict__[elem]
        return data
