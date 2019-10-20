from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, Integer, String, func

db = SQLAlchemy()


class CommonColumns(db.Model):
    __abstract__ = True
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now(), onupdate=func.now())
    _etag = Column(String(40))


class Table1(CommonColumns):
    __tablename__ = "table1"
    id = Column(String(255), primary_key=True)


class Table2(CommonColumns):
    __bind_key__ = 'db2'
    __tablename__ = "table2"
    id = Column(Integer, primary_key=True)
