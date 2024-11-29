from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.ext.declarative import declarative_base


class BaseModel(object):
    """
    Master Eve model for SQLALchemy. It provides common columns such as
    _created, _updated, and _etag.
    """
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now(), onupdate=func.now())
    _etag = Column(String(40))


BaseModel = declarative_base(cls=BaseModel)
