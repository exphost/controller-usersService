from flask import request, current_app
import secrets
import string
import requests


def name_allowed(name):
    return name not in ['k8s-admins',
                        'argo-admins',
                        'grafana-admins']


def org_required(fn):
    def wrapper(*args, **kwargs):
        org = request.args.get('org', None)
        if not org:
            return 'Org required', 400
        return fn(*args, **kwargs)
    return wrapper


def generate_password(length=16):
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    symbols = string.punctuation
    all = lower + upper + num + symbols
    return ''.join(secrets.choice(all) for i in range(length))


def auth_required(fn):
    def wrapper(*args, **kwargs):
        if not request.headers.get('Authorization', None):
            return {'error': 'Not authenticated'}, 401
        claims_response = requests.post(
            current_app.config['AUTHSERVICE_ENDPOINT'] + '/api/auth/v1/token/validate',  # noqa E501
            headers={'Authorization': request.headers['Authorization']}
        )
        if claims_response.status_code != 200:
            return {'error': 'Not authenticated'}, 401
        print("AAA: ", claims_response.json())
        request.user = claims_response.json()['claims']['name']
        return fn(*args, **kwargs)
    return wrapper


def has_access_to_org(fn):
    def wrapper(*args, **kwargs):
        if not request.headers.get('Authorization', None):
            return {'error': 'Not authenticated'}, 401
        claims_response = requests.post(
            current_app.config['AUTHSERVICE_ENDPOINT'] + '/api/auth/v1/token/validate',  # noqa E501
            headers={'Authorization': request.headers['Authorization']}
        )
        if claims_response.status_code != 200:
            return {'error': 'Not authenticated'}, 401
        print("AAA: ", claims_response.json())
        groups = claims_response.json()['claims']['groups']

        if request.method == "POST":
            org = request.args['org']
        elif request.method == "GET":
            org = request.args['org']
        else:
            return {'error': 'Method not implemented'}, 501
        if org not in groups:
            return {'error': 'Org not permitted'}, 403
        return fn(*args, **kwargs)
    return wrapper
