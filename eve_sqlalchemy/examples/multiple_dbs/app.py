from eve import Eve

from eve_sqlalchemy import SQL
from eve_sqlalchemy.examples.multiple_dbs.domain import db as flask_db
from eve_sqlalchemy.validation import ValidatorSQL

app = Eve(validator=ValidatorSQL, data=SQL)
db = app.data.driver
flask_db.Model.metadata.bind = db.engine
db.Model = flask_db.Model
db.create_all()

# using reloader will destroy in-memory sqlite db
app.run(debug=True, use_reloader=False)
