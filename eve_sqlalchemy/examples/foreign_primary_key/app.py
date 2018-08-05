from eve import Eve

from eve_sqlalchemy import SQL
from eve_sqlalchemy.examples.foreign_primary_key.domain import Base, Lock, Node
from eve_sqlalchemy.validation import ValidatorSQL

app = Eve(validator=ValidatorSQL, data=SQL)

db = app.data.driver
Base.metadata.bind = db.engine
db.Model = Base
db.create_all()

nodes = [Node(), Node()]
locks = [Lock(node=nodes[1])]
db.session.add_all(nodes + locks)
db.session.commit()

# using reloader will destroy in-memory sqlite db
app.run(debug=True, use_reloader=False)
