from flask import request


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
