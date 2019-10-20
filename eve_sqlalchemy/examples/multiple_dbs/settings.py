from eve_sqlalchemy.config import DomainConfig, ResourceConfig
from eve_sqlalchemy.examples.multiple_dbs.domain import Table1, Table2

DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']

SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/db1.sqlite'
SQLALCHEMY_BINDS = {
    'db2': 'sqlite:////tmp/db2.sqlite'
}

# The following two lines will output the SQL statements executed by
# SQLAlchemy. This is useful while debugging and in development, but is turned
# off by default.
# --------
# SQLALCHEMY_ECHO = True
# SQLALCHEMY_RECORD_QUERIES = True

# The default schema is generated using DomainConfig:
DOMAIN = DomainConfig({
    'table1': ResourceConfig(Table1),
    'table2': ResourceConfig(Table2)
}).render()
