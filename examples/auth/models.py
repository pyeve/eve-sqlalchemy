import hashlib
from itsdangerous import (
    BadSignature, SignatureExpired,
    TimedJSONWebSignatureSerializer as Serializer,
)
from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, String, Table, func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property, relationship, validates


Base = declarative_base()

SECRET_KEY = 'this-is-my-super-sercret-key'


class CommonColumns(Base):
    __abstract__ = True
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now())
    _etag = Column(String(40))


class People(CommonColumns):
    __tablename__ = 'people'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(80))
    lastname = Column(String(120))
    fullname = column_property(firstname + " " + lastname)


class Invoices(CommonColumns):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    numner = Column(Integer)
    people_id = Column(Integer, ForeignKey('people.id'))
    people = relationship(People, uselist=False)


association_table = Table(
    'association', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('user_login', String(80), ForeignKey('users.login')),
)


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))


class User(Base):
    __tablename__ = 'users'
    login = Column(String(120), primary_key=True)
    password = Column(String(120))
    roles = relationship('Role', secondary=association_table, backref='users')

    def generate_auth_token(self, expiration=24 * 60 * 60):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'login': self.login})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
            print(data)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        return data['login']

    def isAuthorized(self, role_names):
        allowed_roles = set(
            [r.name for r in self.roles]).intersection(set(role_names))
        return len(allowed_roles) > 0

    def generate_salt(self):
        return SECRET_KEY

    def encrypt(self, password):
        return str(hashlib.sha1(
                (password + str(self.generate_salt())).encode('utf8')
        ).hexdigest())

    @validates('password')
    def _set_password(self, key, value):
        return self.encrypt(value)

    def check_password(self, password):
        if not self.password:
            return False
        return self.encrypt(password) == self.password
