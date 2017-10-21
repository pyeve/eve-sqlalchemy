from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property, relationship

Base = declarative_base()


class CommonColumns(Base):
    __abstract__ = True
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now(), onupdate=func.now())
    _etag = Column(String(40))


class People(CommonColumns):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(80))
    lastname = Column(String(120))
    fullname = column_property(firstname + " " + lastname)


class Invoices(CommonColumns):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer)
    people_id = Column(Integer, ForeignKey('people.id'))
    people = relationship(People, uselist=False)
