from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, String, Table, func,
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship

Base = declarative_base()


def get_current_user_id():
    return 1


class CommonColumns(Base):
    __abstract__ = True
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now(), onupdate=func.now())
    _etag = Column(String(40))

    @declared_attr
    def created_by_id(cls):
        return Column(Integer,
                      ForeignKey('users.id'),
                      default=get_current_user_id)

    @declared_attr
    def updated_by_id(cls):
        return Column(Integer,
                      ForeignKey('users.id'),
                      default=get_current_user_id,
                      onupdate=get_current_user_id)

    @declared_attr
    def created_by(cls):
        return relationship(
            'Users',
            foreign_keys='{}.created_by_id'.format(cls.__name__))

    @declared_attr
    def updated_by(cls):
        return relationship(
            'Users',
            foreign_keys='{}.updated_by_id'.format(cls.__name__))

    @declared_attr
    def organization(cls):
        return relationship(
            'Organizations',
            primaryjoin='{}.created_by_id==Users.id'.format(cls.__name__),
            secondary='join(Users, Organizations, Users.organization_id == Organizations.id)',  # noqa
            viewonly=True)


class Users(Base):
    __tablename__ = 'users'
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now(), onupdate=func.now())
    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer,
                             ForeignKey('organizations.id'),
                             nullable=False)
    organization = relationship('Organizations',
                                back_populates='users')


class Organizations(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128))
    users = relationship('Users', back_populates='organization')


class Nodes(CommonColumns):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True, autoincrement=True)
