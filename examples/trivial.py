''' Trivial Eve-SQLAlchemy example. '''
from eve import Eve
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property

from eve_sqlalchemy import SQL
from eve_sqlalchemy.decorators import registerSchema
from eve_sqlalchemy.validation import ValidatorSQL

Base = declarative_base()


class People(Base):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(80))
    lastname = Column(String(120))
    fullname = column_property(firstname + " " + lastname)

    @classmethod
    def from_tuple(cls, data):
        """Helper method to populate the db"""
        return cls(firstname=data[0], lastname=data[1])


registerSchema('people')(People)

SETTINGS = {
    'DEBUG': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite://',
    'DOMAIN': {
        'people': People._eve_schema['people'],
    }
}

app = Eve(auth=None, settings=SETTINGS, validator=ValidatorSQL, data=SQL)

# bind SQLAlchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base
db.create_all()

# Insert some example data in the db

test_data = [
    (u'George', u'Washington'),
    (u'John', u'Adams'),
    (u'Thomas', u'Jefferson'),
]

if not db.session.query(People).count():
    for item in test_data:
        db.session.add(People.from_tuple(item))
    db.session.commit()

app.run(debug=True, use_reloader=False)
# using reloader will destroy in-memory sqlite db
