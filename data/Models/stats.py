import sqlalchemy
from sqlalchemy import orm
from data.Sql.db_session import SqlAlchemyBase


class Stats(SqlAlchemyBase):
    __tablename__ = 'statistics'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    player_mail = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.email"), unique=True)

    kills = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    deaths = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    rik = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    hits = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    fires = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    damage = sqlalchemy.Column(sqlalchemy.Float, nullable=True)

    user = orm.relation('User')

    def to_dict(self, only=("player_mail", "kills", "deaths", "rik", "hits", "fires", "damage")):
        data = {}
        for elem in only:
            data[elem] = self.__dict__[elem]
        return data


