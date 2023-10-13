from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
import cracklib
from .helpers import has_access_to_org
from .helpers import generate_password

bp = Blueprint('emails', __name__, url_prefix='/api/users//v1/emails')
api = Api(bp, doc='/')


email_model = api.model(
    'Email',
    {
        'mail': fields.String(
            description="Email",
            required=True,
            example="test@example.com"
        ),
        'cn': fields.String(
            description="Common name",
            required=True,
            example="Kate"
        ),
        'sn': fields.String(
            description="Surname",
            required=True,
            example="Brown"
        ),
        'password': fields.String(
            description="Password",
            required=False,
            example="katekate"
        ),
        'aliases': fields.List(fields.String(
            description="Email",
            required=True,
            example="katebrown@example.com"
        )),
    }
)


@api.route("/", endpoint='emails')
class Email(Resource):
    @api.expect(email_model, validate=True)
    @has_access_to_org
    def post(self):
        domain = request.json.get('mail').split('@')[1]
        org = request.args.get('org')
        token = request.headers.get('Authorization')
        if not current_app.DAODomains.check_domain_access(domain, org, token):
            return 'Unauthorized email domain', 403
        for alias in request.json.get('aliases', []):
            alias_domain = alias.split("@")[1]
            if not current_app.DAODomains.check_domain_access(alias_domain, org, token): # noqa 501
                return 'Unauthorized alias domain', 403
        if not request.json.get('password', None):
            request.json['password'] = generate_password()
        mail = request.json
        try:
            cracklib.FascistCheck(
                request.json['password'],
                current_app.config['PASSWORDS_DICT']
            )
        except ValueError:
            return "Password to simple", 400

        merged_aliases = set(request.json.get('aliases', []))
        merged_aliases.add(request.json.get('mail'))
        merged_aliases = sorted([alias.encode() for alias in merged_aliases])
        mail['aliases'] = merged_aliases
        current_app.DAO.create_email(**mail)
        mail['aliases'] = sorted([alias.decode() for alias in mail['aliases']])
        mail['aliases'].remove(mail['mail'])
        return mail, 201

    @has_access_to_org
    def get(self):
        org = request.args.get('org')
        token = request.headers.get('Authorization')
        domains = current_app.DAODomains.get_domains(org, token)
        emails = []
        for domain in domains:
            emails.extend(current_app.DAO.get_emails(domain['name']))
        return emails, 200
