"""Basic Many-To-Many relationship configuration in SQLAlchemy.

This is taken from the official SQLAlchemy documentation:
https://docs.sqlalchemy.org/en/rel_1_1/orm/basic_relationships.html#many-to-many
"""

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, String, Table, func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now(), onupdate=func.now())
    _etag = Column(String(40))


association_table = Table(
    'association', Base.metadata,
    Column('left_id', Integer, ForeignKey('left.id')),
    Column('right_id', Integer, ForeignKey('right.id'))
)


class Parent(BaseModel):
    __tablename__ = 'left'
    id = Column(Integer, primary_key=True)
    children = relationship("Child", secondary=association_table,
                            backref="parents")


class Child(BaseModel):
    __tablename__ = 'right'
    id = Column(Integer, primary_key=True)
