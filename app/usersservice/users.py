from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
import ldap

bp = Blueprint('users', __name__, url_prefix='/')
api = Api(bp, doc='/')

user_model = api.model(
    'User',
    {
        'login': fields.String(
            description="Login",
            required=True,
            example="testuser"
        ),
        'gn': fields.String(
            description="Given name",
            required=True,
            example="Kate"
        ),
        'sn': fields.String(
            description="Surname",
            required=True,
            example="Brown"
        ),
        'mail': fields.String(
            description="Email",
            required=True,
            example="katebrown@example.com"
        ),
        'password': fields.String(
            description="Password",
            required=True,
            example="katekate"
        ),
    }
)


@api.route("/users/", endpoint='users')
class User(Resource):
    @api.expect(user_model, validate=True)
    def post(self):
        api.logger.info("Creating user: {user}".format(
            user=request.json.get('login', "__not_present")
        ))
        try:
            current_app.DAO.create_user(**request.json)
        except ldap.ALREADY_EXISTS:
            return "User already exists", 409
