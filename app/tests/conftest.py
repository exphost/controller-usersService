import os

import pytest
from usersservice import create_app
import usersservice
from tests.mock_dao import MockDAO


@pytest.fixture
def app(mocker):
    mocker.patch.object(usersservice, "DAO", MockDAO)
    os.environ['LDAP_BASE'] = 'dc=example,dc=com'
    app = create_app()
    yield app


@pytest.fixture
def app_debug(mocker):
    mocker.patch.object(usersservice, "DAO", MockDAO)
    os.environ['LDAP_BASE'] = 'dc=example,dc=com'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
