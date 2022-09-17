from flask import request
import secrets
import string
import base64
import json


def name_allowed(name):
    return name not in ['k8s-admins',
                        'argo-admins',
                        'grafana-admins']


def auth_required(fn):
    def wrapper(*args, **kwargs):
        if not request.headers.get('X-User', None):
            return {'error': 'Not authenticated'}, 401
        return fn(*args, **kwargs)
    return wrapper


def auth_required_v2(fn):
    def wrapper(*args, **kwargs):
        user = request.headers.get('Authorization', None)
        if not user:
            return 'Not authenticated', 401
        user = user.split()
        if user[0] != "Bearer":
            return 'Not authenticated', 401
        if len(user) != 2:
            return 'Not authenticated', 401
        return fn(*args, **kwargs)
    return wrapper


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


def org_authorized(fn):
    def wrapper(*args, **kwargs):
        org = request.args.get('org', None)
        user = request.headers.get('Authorization', None)
        user = user.split(" ")[1].split(".")[1]
        user = base64.b64decode(user)
        user = json.loads(user)
        if org not in user['groups']:
            return "Org not authorized", 403
        return fn(*args, **kwargs)
    return wrapper
