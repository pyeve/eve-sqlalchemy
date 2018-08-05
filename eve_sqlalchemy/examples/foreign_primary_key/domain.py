from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now(), onupdate=func.now())
    _etag = Column(String(40))


class Node(BaseModel):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True, autoincrement=True)
    lock = relationship('Lock', uselist=False)


class Lock(BaseModel):
    __tablename__ = 'lock'
    node_id = Column(Integer, ForeignKey('node.id'),
                     primary_key=True, nullable=False)
    node = relationship(Node, uselist=False, back_populates='lock')
