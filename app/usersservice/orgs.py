from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
import ldap
from .helpers import name_allowed

bp = Blueprint('groups', __name__, url_prefix='/users')
api = Api(bp, doc='/')

org_model = api.model(
    'Group',
    {
        'name': fields.String(
            description="Org name",
            required=True,
            example="simpleCompany"
        ),
        'members': fields.List(
            fields.String(
                description="member",
                required=True
            ),
            description="Extra members of the org (except owner)",
            required=False,
            example="Kate"
        ),
    }
)


@api.route("/groups/", endpoint='groups')
class Org(Resource):
    @api.expect(org_model, validate=True)
    def post(self):
        user = request.headers.get("X-User", None)
        if not user:
            return "Not Authorized", 401
        if not name_allowed(request.json['name']):
            return "Name not allowed", 403
        api.logger.info("Creating org: {org}".format(
            org=request.json.get('cn', "__not_present")
        ))
        org_obj = {
            'name': request.json['name'],
            'owner': user,
            'members': request.json.get("members", []) + [user, ]
        }
        try:
            current_app.DAO.create_group(**org_obj)

            return org_obj, 201
        except ldap.ALREADY_EXISTS:
            return "Org already exists", 409
