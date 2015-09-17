import hashlib

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import column_property, relationship, backref
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import String
from eve_sqlalchemy.decorators import registerSchema
from eve_sqlalchemy import db

Base = declarative_base()
db.Model = Base


class CommonColumns(Base):
    """
    Master SQLAlchemy Model. All the SQL tables defined for the application
    should inherit from this class. It provides common columns such as
    _created, _updated and _id.

    WARNING: the _id column name does not respect Eve's setting for custom
    ID_FIELD.
    """
    __abstract__ = True
    _created = Column(DateTime,  default=func.now())
    _updated = Column(DateTime,  default=func.now(), onupdate=func.now())
    _etag = Column(String)
    # TODO: make this comply to Eve's custom ID_FIELD setting
    _id = Column(Integer, primary_key=True)

    def __init__(self, *args, **kwargs):
        h = hashlib.sha1()
        self._etag = h.hexdigest()
        super(CommonColumns, self).__init__(*args, **kwargs)


@registerSchema('people')
class People(CommonColumns):
    __tablename__ = 'people'
    firstname = Column(String(80), unique=True)
    lastname = Column(String(120))
    fullname = column_property(firstname + " " + lastname)
    prog = Column(Integer)
    born = Column(DateTime)
    title = Column(String(20), default='Mr.')

    @classmethod
    def from_tuple(cls, data):
        return cls(firstname=data[0], lastname=data[1], prog=data[2])


@registerSchema('notes')
class Notes(CommonColumns):
    __tablename__ = 'notes'
    people_id = Column(Integer, ForeignKey('people._id'), nullable=False)
    content = Column(String(120))


@registerSchema('invoices')
class Invoices(CommonColumns):
    __tablename__ = 'invoices'
    number = Column(Integer)
    people_id = Column(Integer, ForeignKey('people._id'))
    people = relationship(People, backref='invoices_collection')


@registerSchema('payments')
class Payments(CommonColumns):
    __tablename__ = 'payments'
    number = Column(Integer)
    string = Column(String(80))


class Products(CommonColumns):
    __tablename__ = 'products'
    name = Column(String(80))

    keywords = association_proxy(
        'products_keywords_assoc', 'keyword',
        creator=lambda keyword_id: ProductsKeywords(keyword_id=keyword_id)
    )


class Keywords(CommonColumns):
    __tablename__ = 'keywords'

    kw = Column(String(80))


class ProductsKeywords(Base):
    __tablename__ = 'products_keywords'
    product_id = Column(Integer, ForeignKey('products._id'), primary_key=True)
    keyword_id = Column(Integer, ForeignKey('keywords._id'), primary_key=True)

    product = relationship(
        'Products',
        backref=backref('products_keywords_assoc',
                        cascade="all,delete-orphan")
    )
    keyword = relationship('Keywords')

# Since the corresponding mappers of the following classes are not yet fully
# configured, we need to make a direct call the registerSchema() decorator.

# Note(Kevin Roy): Maybe we should use mapper.configure_mappers() and the
# decorator registerSchema should be triggered for each model class on the
# Mappers event 'after_configured'.

registerSchema('products')(Products)
registerSchema('keywords')(Keywords)
