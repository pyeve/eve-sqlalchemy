# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, LargeBinary,
    PickleType, String, func,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from eve_sqlalchemy import db
from eve_sqlalchemy.decorators import registerSchema

Base = declarative_base()
db.Model = Base


class CommonColumns(Base):
    """
    Master SQLAlchemy Model. All the SQL tables defined for the application
    should inherit from this class. It provides common columns such as
    _created, _updated and _id.

    WARNING: the _id column name does not respect Eve's setting for custom
    ID_FIELD.
    """
    __abstract__ = True
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now(), onupdate=func.now())
    _etag = Column(String)

    def __init__(self, *args, **kwargs):
        h = hashlib.sha1()
        self._etag = h.hexdigest()
        super(CommonColumns, self).__init__(*args, **kwargs)


@registerSchema('disabled_bulk')
class DisabledBulk(CommonColumns):
    __tablename__ = 'disabled_bulk'
    _id = Column(Integer, primary_key=True)
    string_field = Column(String(25))


class InvoicingContacts(Base):
    __tablename__ = 'invoicing_contacts'
    invoice_id = Column(Integer, ForeignKey('invoices._id'), primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts._id'), primary_key=True)
    contact = relationship('Contacts')


@registerSchema('contacts')
class Contacts(CommonColumns):
    __tablename__ = 'contacts'
    _id = Column(Integer, primary_key=True)
    ref = Column(String(25), unique=True, nullable=False)
    media = Column(LargeBinary)
    prog = Column(Integer)
    role = Column(PickleType)
    rows = Column(PickleType)
    alist = Column(PickleType)
    location = Column(PickleType)
    born = Column(DateTime)
    tid = Column(Integer)
    title = Column(String(20), default='Mr.')
    # id_list
    # id_list_of_dict
    # id_list_fixed_len
    dependency_field1 = Column(String(25), default='default')
    dependency_field2 = Column(String(25))
    dependency_field3 = Column(String(25))
    read_only_field = Column(String(25), default='default')
    # dict_with_read_only
    key1 = Column(String(25))
    propertyschema_dict = Column(PickleType)
    valueschema_dict = Column(PickleType)
    aninteger = Column(Integer)
    afloat = Column(Float)
    anumber = Column(Float)
    username = Column(String(25), default='')
    # additional fields for Eve-SQLAlchemy tests
    abool = Column(Boolean)


@registerSchema('invoices')
@registerSchema('required_invoices')
class Invoices(CommonColumns):
    __tablename__ = 'invoices'
    _id = Column(Integer, primary_key=True)
    inv_number = Column(String(25))
    person_id = Column(Integer, ForeignKey('contacts._id'))
    person = relationship(Contacts)
    invoicing_contacts = association_proxy(
        'invoicing_contacts_assoc', 'contact',
        creator=lambda contact_id: InvoicingContacts(contact_id=contact_id))
    invoicing_contacts_assoc = relationship('InvoicingContacts')


@registerSchema('empty')
class Empty(CommonColumns):
    __tablename__ = 'empty'
    _id = Column(Integer, primary_key=True)
    inv_number = Column(String(25))


class DepartmentsContacts(Base):
    __tablename__ = 'department_contacts'
    department_id = Column(Integer, ForeignKey('departments._id'),
                           primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts._id'), primary_key=True)
    # departments = relationship('Departments',
    #                            backref=backref('departments_contacts_assoc',
    #                                            cascade='all,delete-orphan'))
    contact = relationship('Contacts')


class CompaniesDepartments(Base):
    __tablename__ = 'companies_departments'
    company_id = Column(Integer, ForeignKey('companies._id'), primary_key=True)
    department_id = Column(Integer, ForeignKey('departments._id'),
                           primary_key=True)
    # companies = relationship('Companies',
    #                          backref=backref('companies_departments_assoc',
    #                                          cascade='all,delete-orphan'))
    department = relationship('Departments')


@registerSchema('departments')
class Departments(CommonColumns):
    __tablename__ = 'departments'
    _id = Column(Integer, primary_key=True)
    title = Column(String(25))
    members = association_proxy(
        'departments_contacts_assoc', 'contact',
        creator=lambda contact_id: DepartmentsContacts(
            contact_id=contact_id))
    departments_contacts_assoc = relationship('DepartmentsContacts')


@registerSchema('companies')
class Companies(CommonColumns):
    __tablename__ = 'companies'
    _id = Column(Integer, primary_key=True)
    holding_id = Column(String(16), ForeignKey('companies._id'))
    holding = relationship('Companies', remote_side=[_id])
    departments = association_proxy(
        'companies_departments_assoc', 'department',
        creator=lambda department_id: CompaniesDepartments(
            department_id=department_id))
    companies_departments_assoc = relationship('CompaniesDepartments')


@registerSchema('payments')
class Payments(CommonColumns):
    __tablename__ = 'payments'
    _id = Column(Integer, primary_key=True)
    a_string = Column(String(10))
    a_number = Column(Integer)


@registerSchema('internal_transactions')
class InternalTransactions(CommonColumns):
    __tablename__ = 'internal_transactions'
    _id = Column(Integer, primary_key=True)
    internal_string = Column(String(10))
    internal_number = Column(Integer)


@registerSchema('login')
class Login(CommonColumns):
    __tablename__ = 'login'
    _id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(32), nullable=False)


@registerSchema('products')
class Products(CommonColumns):
    __tablename__ = 'products'
    sku = Column(String(16), primary_key=True)
    title = Column(String(32))
    parent_product_sku = Column(String(16), ForeignKey('products.sku'))
    parent_product = relationship('Products', remote_side=[sku])
