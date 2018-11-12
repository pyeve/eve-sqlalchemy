from eve import Eve

from eve_sqlalchemy import SQL
from eve_sqlalchemy.examples.viewonly.domain import Base, Users, Organizations
from eve_sqlalchemy.validation import ValidatorSQL

app = Eve(validator=ValidatorSQL, data=SQL)

db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base
db.create_all()

db.session.add(Organizations(name='ACME', users=[Users(), Users()]))
db.session.add(Organizations(name='Eve', users=[Users()]))
db.session.commit()

# using reloader will destroy in-memory sqlite db
app.run(debug=True, use_reloader=False)
