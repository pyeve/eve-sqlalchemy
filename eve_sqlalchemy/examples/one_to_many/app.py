from eve import Eve

from eve_sqlalchemy import SQL
from eve_sqlalchemy.examples.one_to_many.domain import Base, Child, Parent
from eve_sqlalchemy.validation import ValidatorSQL

app = Eve(validator=ValidatorSQL, data=SQL)

db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base

# create database schema on startup and populate some example data
db.create_all()
db.session.add_all([Parent(children=[Child() for k in range(n)])
                    for n in range(10)])
db.session.commit()

# using reloader will destroy the in-memory sqlite db
app.run(debug=True, use_reloader=False)
