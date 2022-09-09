import os

import pytest
from usersservice import create_app


@pytest.fixture
def app(mocker):
    mocker.patch('ldap.initialize')
    os.environ['LDAP_BASE'] = 'dc=example,dc=com'
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
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
