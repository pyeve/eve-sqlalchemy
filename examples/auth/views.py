import json
import base64
from flask import request, jsonify
from werkzeug.exceptions import Unauthorized
from models import User


def register_views(app):
    @app.route('/login', methods=['POST'])
    def login(**kwargs):
        data = request.get_json()
        login = data.get('username')
        password = data.get('password')
        if not login or not password:
            raise Unauthorized('Wrong username and/or password.')
        else:
            user = app.data.driver.session.query(User).get(login)
            if user and user.check_password(password):
                token = user.generate_auth_token()
                return jsonify({'token': token.decode('ascii')})
        raise Unauthorized('Wrong username and/or password.')
