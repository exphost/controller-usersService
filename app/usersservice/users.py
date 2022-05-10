from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
import ldap
from .helpers import auth_required, name_allowed

bp = Blueprint('users', __name__, url_prefix='/users')
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
        if not name_allowed(request.json['login']):
            return "Name not allowed", 403
        api.logger.info("Creating user: {user}".format(
            user=request.json.get('login', "__not_present")
        ))
        try:
            current_app.DAO.create_user(**request.json)
            group_params = {
                'name': request.json['login'],
                'owner': request.json['login'],
                'members': [request.json['login']],
            }
            current_app.DAO.create_group(**group_params)
            return request.json, 201
        except ldap.ALREADY_EXISTS:
            return "User already exists", 409


@api.route("/userinfo", endpoint="userinfo")
class UserInfo(Resource):
    @auth_required
    def get(self):
        user = current_app.DAO.get_user(request.headers.get('X-User'))
        api.logger.debug(f"Getting userinfo: {user}")
        if not user:
            return None, 404

        return {'username': user['cn'],
                'groups': user['groups'],
                'sn': user['sn'],
                'gn': user['gn'],
                'mail': user['mail']}
