import os

import pytest
from usersservice import create_app

from functools import partial

import yaml
import json
import requests
from urllib import parse
from openapi_core import create_spec
from openapi_core.validation.response.validators import ResponseValidator
from openapi_core.validation.request.validators import RequestValidator
from openapi_core.validation.response.datatypes import OpenAPIResponse
from openapi_core.validation.request.datatypes import OpenAPIRequest, RequestParameters # noqa 501


USER="eyJpc3MiOiAiaHR0cHM6Ly9hdXRoLmdhdGV3YXktMzktZGV2LXBhc3MtdXNlci0wNWxzamMuY2kuZXhwaG9zdC5wbC9kZXgiLCAic3ViIjogIkNnZDBaWE4wTFhCeUVnUnNaR0Z3IiwgImF1ZCI6ICJleHBob3N0LWNvbnRyb2xsZXIiLCAiZXhwIjogMTY1MjE4MDM1MywgImlhdCI6IDE2NTIwOTM5NTMsICJhdF9oYXNoIjogIjc1a0NUUkRxTFFMU19XWjgyVUtXZGciLCAiZW1haWwiOiAidGVzdC1wckBtYWlsLnJ1IiwgImVtYWlsX3ZlcmlmaWVkIjogdHJ1ZSwgImdyb3VwcyI6IFsidGVzdC11c2VyIiwgInRlc3Qtb3JnIl0sICJuYW1lIjogInRlc3QtdXNlciJ9" # noqa 501
USER_TOKEN="eyJhbGciOiJSUzI1NiIsImtpZCI6IjRhZmIzZWVmNDFmMjI3OTYwMDYxZDkxNzY0NTI4YzYwMzcwZDI3ZDcifQ.eyJpc3MiOiAiaHR0cHM6Ly9hdXRoLmdhdGV3YXktMzktZGV2LXBhc3MtdXNlci0wNWxzamMuY2kuZXhwaG9zdC5wbC9kZXgiLCAic3ViIjogIkNnZDBaWE4wTFhCeUVnUnNaR0Z3IiwgImF1ZCI6ICJleHBob3N0LWNvbnRyb2xsZXIiLCAiZXhwIjogMTY1MjE4MDM1MywgImlhdCI6IDE2NTIwOTM5NTMsICJhdF9oYXNoIjogIjc1a0NUUkRxTFFMU19XWjgyVUtXZGciLCAiZW1haWwiOiAidGVzdC1wckBtYWlsLnJ1IiwgImVtYWlsX3ZlcmlmaWVkIjogdHJ1ZSwgImdyb3VwcyI6IFsidGVzdC11c2VyIiwgInRlc3Qtb3JnIl0sICJuYW1lIjogInRlc3QtdXNlciJ9.XXX" # noqa 501


def make_tested_request(
        client,
        url,
        method,
        headers,
        body={},
        mime='application/json',
        requestValidator=None,
        responseValidator=None):
    url_p = parse.urlsplit(url)
    api_request_parameters = RequestParameters(
        header=headers,
        query=dict(parse.parse_qsl(url_p.query))
    )
    api_request = OpenAPIRequest(
        full_url_pattern=url_p.path,
        method=method,
        parameters=api_request_parameters,
        body=json.dumps(body),
        mimetype=mime
    )
    result = requestValidator.validate(api_request)
    result.raise_for_errors()

    response = client.__getattribute__(method)(
        url,
        json=json.loads(api_request.body),
        headers=api_request_parameters.header
    )
    print(api_request_parameters)
    print(api_request)
    print(response.data)
    api_response = OpenAPIResponse(
        data=json.dumps(response.json),
        status_code=response.status_code,
        mimetype=response.mimetype
    )
    result = responseValidator.validate(api_request, api_response)
    result.raise_for_errors()
    return response


@pytest.fixture
def app(mocker):
    mocker.patch('ldap.initialize')
    os.environ['LDAP_BASE'] = 'dc=example,dc=com'
    os.environ['APIGATEWAY_URL'] = 'http://127.0.0.1:8001'
    os.environ['AUTHSERVICE_ENDPOINT'] = 'http://127.0.0.1:8000'
    app = create_app()
    yield app


@pytest.fixture
def app_debug(mocker):
    os.environ['LDAP_BASE'] = 'dc=example,dc=com'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    mocker.patch('ldap.initialize')
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    client = app.test_client()
    with open('apispec/usersservice.yml', 'r') as spec_file:
        spec_dict = yaml.safe_load(spec_file)
    spec = create_spec(spec_dict)
    responseValidator = ResponseValidator(spec)
    requestValidator = RequestValidator(spec)
    client.make_tested_request = partial(
        make_tested_request,
        requestValidator=requestValidator,
        responseValidator=responseValidator)
    return client


@pytest.fixture
def domains_mock(app, mocker):
    response = {
        'data': {'domain': {'domains': [
            {'name': 'example.com', 'org': 'test-org'},
            {'name': 'local.domain', 'org': 'test-org'}
        ]}},
        "claims": {"iss": "https://auth.usersservice-22-dev-authservice-va444e.ci.exphost.pl/dex", "sub": "CgR0ZXN0EgRsZGFw", "aud": "exphost-controller", "exp": 1697202958, "iat": 1697116558, "at_hash": "XDGcSLVlPMa-gGIok8d62A", "email": "test@mail.ru", "email_verified": True, "groups": ["test-org"], "name": "test"}} # workaround for auth_required and mock problem # noqa 501
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = json.dumps(response).encode()
    mocker.patch.object(
        app.DAODomains.requests,
        'post',
        return_value=mock_response
    )


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
