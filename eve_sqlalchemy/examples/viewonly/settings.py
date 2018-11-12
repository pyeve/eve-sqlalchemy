from eve_sqlalchemy.config import DomainConfig, ResourceConfig
from eve_sqlalchemy.examples.viewonly.domain import Users, Organizations, Nodes

DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite://'
SQLALCHEMY_TRACK_MODIFICATIONS = False
RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH']

# The following two lines will output the SQL statements executed by
# SQLAlchemy. This is useful while debugging and in development, but is turned
# off by default.
# --------
# SQLALCHEMY_ECHO = True
# SQLALCHEMY_RECORD_QUERIES = True

# The default schema is generated using DomainConfig:
DOMAIN = DomainConfig({
    'users': ResourceConfig(Users),
    'organizations': ResourceConfig(Organizations),
    'nodes': ResourceConfig(Nodes),
}).render()
