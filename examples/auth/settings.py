from eve_sqlalchemy.config import DomainConfig, ResourceConfig
from models import Invoices, People

DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite://'
SQLALCHEMY_TARCK_MODIFICATIONS = False
RESOURCE_METHODS = ['GET', 'POST']

ALLOWED_ROLES = ['admin']

DOMAIN = DomainConfig({
    'people': ResourceConfig(People),
    'invoice': ResourceConfig(Invoices)
}).render()

DOMAIN['people'].update({
    'item_title': 'person',
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'resource_methods': ['GET', 'POST', 'DELETE']
})
