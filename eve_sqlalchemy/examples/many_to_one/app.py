from eve import Eve

from eve_sqlalchemy import SQL
from eve_sqlalchemy.examples.many_to_one.domain import Base, Child, Parent
from eve_sqlalchemy.validation import ValidatorSQL

app = Eve(validator=ValidatorSQL, data=SQL)

db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base
db.create_all()

children = [Child(), Child()]
parents = [Parent(child=children[n % 2]) for n in range(10)]
db.session.add_all(parents)
db.session.commit()

# using reloader will destroy in-memory sqlite db
app.run(debug=True, use_reloader=False)
