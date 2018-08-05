from eve import Eve

from eve_sqlalchemy import SQL
from eve_sqlalchemy.examples.simple.tables import Base, Invoices, People
from eve_sqlalchemy.validation import ValidatorSQL

app = Eve(validator=ValidatorSQL, data=SQL)

# bind SQLAlchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base
db.create_all()

# Insert some example data in the db
if not db.session.query(People).count():
    from eve_sqlalchemy.examples.simple import example_data
    for item in example_data.test_data:
        db.session.add(People(firstname=item[0], lastname=item[1]))
    db.session.add(Invoices(number=42, people_id=1))
    db.session.commit()

# using reloader will destroy in-memory sqlite db
app.run(debug=True, use_reloader=False)
