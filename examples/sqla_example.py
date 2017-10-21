from eve import Eve
from examples.tables import Base, People

from eve_sqlalchemy import SQL
from eve_sqlalchemy.validation import ValidatorSQL


app = Eve(validator=ValidatorSQL, data=SQL)

# bind SQLAlchemy
db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base
db.create_all()

# Insert some example data in the db
if not db.session.query(People).count():
    from examples import example_data
    for item in example_data.test_data:
        db.session.add(People.from_tuple(item))
    db.session.commit()

# using reloader will destroy in-memory sqlite db
app.run(debug=True, use_reloader=False)
