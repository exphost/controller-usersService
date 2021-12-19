#!/usr/bin/env python
import os
from flask import Flask, request
from flask_restx import Api, Resource, fields

from dao import DAO

app = Flask(__name__)

api = Api(app)

user_model = api.model(
    'User',
    {
        'login': fields.String(description="Login", required=True, title="Some title"),
        'gn': fields.String(description="Given name", required=True, example="Kate"),
        'sn': fields.String(description="Surname", required=True),
        'mail': fields.String(description="Email", required=True),
        'password': fields.String(description="Password", required=True),
    }
)

@api.route('/users')
class User(Resource):
    @api.expect(user_model)
    def post(self):
        """ Create user """
        app.logger.info("Creating user: {user}".format(user=request.json.get('login', "__not_present")))
        dao.create_user(**request.json)

dao = DAO(base=os.environ['LDAP_BASE'], uri=os.environ['LDAP_URI'], dn=os.environ['LDAP_DN'], password=os.environ['LDAP_PASSWORD'])

if __name__ == "__main__":
    app.run()
