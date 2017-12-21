from eve import Eve
from eve.auth import TokenAuth
from eve_sqlalchemy import SQL
from eve_sqlalchemy.validation import ValidatorSQL
from models import Role, User, Base
from views import register_views
import pymysql

pymysql.install_as_MySQLdb()


class TokenAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        login = User.verify_auth_token(token)
        if login and allowed_roles:
            user = app.data.driver.session.query(User).get(login)
            return user.isAuthorized(allowed_roles)
        else:
            return False

if __name__ == '__main__':
    app = Eve(auth=TokenAuth, validator=ValidatorSQL, data=SQL)
    db = app.data.driver
    Base.metadata.bind = db.engine
    db.Model = Base
    db.create_all()
    if not db.session.query(User).count():
        r = Role(name='admin')
        db.session.add(r)
        db.session.commit()
        db.session.add(User(login='aa', password='bb', roles=[r]))
        db.session.commit()
    register_views(app)
    app.run(debug=True)
