import ldap
from .conftest import USER_TOKEN


def test_create_email(app, client, mocker, domains_mock):
    response = client.make_tested_request(
        client,
        '/v1/emails/?org=test-org',
        'post',
        {'Authorization': 'Bearer ' + USER_TOKEN},
        {
            'mail': 'test-box@example.com',
            'cn': 'test-box',
            'sn': 'testing',
            'password': 'tesTpaSs*&^j',
            'aliases': ['test-box-alias@example.com']
        }
    )
    assert response.status_code == 201
    assert response.json == {
                            'mail': 'test-box@example.com',
                            'cn': 'test-box',
                            'sn': 'testing',
                            'aliases': ['test-box-alias@example.com'],
                            'password': 'tesTpaSs*&^j'}
    app.DAO.ldap.add_s.assert_called_once_with(
        'maildrop=test-box@example.com,ou=mails,dc=example,dc=com',
        [
            ('objectClass', [b'person', b'postfixUser']),
            ('cn', b'test-box'),
            ('sn', b'testing'),
            ('maildrop', b'test-box@example.com'),
            ('mailacceptinggeneralid', [
                b'test-box-alias@example.com',
                b'test-box@example.com',
            ]),
            ('userPassword', mocker.ANY),
        ])


def test_create_email_random_pass(app, client, mocker, domains_mock):
    response = client.make_tested_request(
        client,
        '/v1/emails/?org=test-org',
        'post',
        {'Authorization': 'Bearer ' + USER_TOKEN},
        {
            'mail': 'test-box@example.com',
            'cn': 'test-box',
            'sn': 'testing',
            'aliases': ['test-box-alias@example.com']
        }
    )
    assert response.status_code == 201
    assert len(response.json['password']) > 0
#    ret_json = response.json
#    ret_json['password'] = 'ignore_randommm'
    assert response.json == {
        'mail': 'test-box@example.com',
        'cn': 'test-box',
        'sn': 'testing',
        'password': mocker.ANY,
        'aliases': [
            'test-box-alias@example.com',
        ],
        }
    app.DAO.ldap.add_s.assert_called_once_with(
        'maildrop=test-box@example.com,ou=mails,dc=example,dc=com',
        [
            ('objectClass', [b'person', b'postfixUser']),
            ('cn', b'test-box'),
            ('sn', b'testing'),
            ('maildrop', b'test-box@example.com'),
            ('mailacceptinggeneralid', [
                b'test-box-alias@example.com',
                b'test-box@example.com',
            ]),
            ('userPassword', mocker.ANY),
        ])


def test_create_email_missing_attributes(app, client, mocker, domains_mock):
    response = client.post(
        '/v1/emails/?=test-org',
        headers={'Authorization': 'Bearer ' + USER_TOKEN}
    )
    assert response.status_code == 400

    response = client.post(
        '/v1/emails/?test-org',
        json={
            'mail': 'test-box@example.com',
            'sn': 'testing',
            'password': 'tesTpaSs*&^j',
            'aliases': ['test-box-alias@example.com']
        },
        headers={'Authorization': 'Bearer ' + USER_TOKEN}
    )
    assert response.status_code == 400

    response = client.post(
        '/v1/emails/?org=test-org',
        json={
            'mail': 'test-box@example.com',
            'cn': 'test-box',
            'password': 'tesTpaSs*&^j',
            'aliases': ['test-box-alias@example.com']
        },
        headers={'Authorization': 'Bearer ' + USER_TOKEN}
    )
    assert response.status_code == 400

    response = client.post(
        '/v1/emails/?org=test-org',
        json={
            'cn': 'test-box',
            'sn': 'testing',
            'password': 'tesTpaSs*&^j',
            'aliases': ['test-box-alias@example.com']
        },
        headers={'Authorization': 'Bearer ' + USER_TOKEN}
    )
    assert response.status_code == 400


def test_create_email_unauthorized_org(app, client, mocker, domains_mock):
    response = client.make_tested_request(
        client,
        '/v1/emails/?org=some-org',
        'post',
        {'Authorization': 'Bearer ' + USER_TOKEN},
        {
            'mail': 'test-box@domain.com',
            'cn': 'test-box',
            'sn': 'testing',
            'password': 'tesTpaSs*&^j',
        }
    )
    assert response.status_code == 403


def test_create_email_to_simple_password(app, client, mocker, domains_mock):
    response = client.make_tested_request(
        client,
        '/v1/emails/?org=test-org',
        'post',
        {'Authorization': 'Bearer ' + USER_TOKEN},
        {
            'mail': 'test-box@example.com',
            'cn': 'test-box',
            'sn': 'testing',
            'password': 'testpass',
            'aliases': ['test-box-alias@example.com']
        }
    )
    assert response.status_code == 400


def test_create_email_unauthorized_domain(app, client, mocker, domains_mock):
    response = client.make_tested_request(
        client,
        '/v1/emails/?org=test-org',
        'post',
        {'Authorization': 'Bearer ' + USER_TOKEN},
        {
            'mail': 'test-box@example.pl',
            'cn': 'test-box',
            'sn': 'testing',
            'password': 'tesTpaSs*&^j',
            'aliases': ['test-box-alias@example.com']
        }
    )
    assert response.status_code == 403


def test_create_email_unauthenticated(app, client, mocker, domains_mock):
    response = client.post(
        "/v1/emails/?org=test-org",
        json={
            'mail': 'test-box@example.com',
            'cn': 'test-box',
            'sn': 'testing',
            'password': 'tesTpaSs*&^j',
            'aliases': ['test-box-alias@example.com']
        }
    )
    assert response.status_code == 401


def test_create_email_unauthorized_domain_aliases(app, client, mocker, domains_mock): # noqa 501
    response = client.make_tested_request(
        client,
        '/v1/emails/?org=test-org',
        'post',
        {'Authorization': 'Bearer ' + USER_TOKEN},
        {
            'mail': 'test-box@example.com',
            'cn': 'test-box',
            'sn': 'testing',
            'password': 'tesTpaSs*&^j',
            'aliases': ['test-box-alias@example.pl']
        }
    )
    assert response.status_code == 403


def test_get_emails(app, client, mocker, domains_mock):
    response = client.make_tested_request(
        client,
        "/v1/emails/?org=test-org",
        "get",
        {'Authorization': 'Bearer ' + USER_TOKEN}
    )
    mock1 = mocker.call(
        'ou=mails,dc=example,dc=com',
        ldap.SCOPE_SUBTREE,
        "(mailacceptinggeneralid=*@example.com)"
    )
    mock2 = mocker.call(
        'ou=mails,dc=example,dc=com',
        ldap.SCOPE_SUBTREE,
        "(mailacceptinggeneralid=*@local.domain)"
    )
    calls = [mock1, mock2]

    app.DAO.ldap.search_s.assert_has_calls(calls, any_order=True)
    assert response.status_code == 200


def test_get_emails_missing_auth(app, client, mocker, domains_mock):
    response = client.get(
        "/v1/emails/?org=test-org",
    )
    assert response.status_code == 401


def test_get_emails_unauthorized(app, client, mocker, domains_mock):
    response = client.make_tested_request(
        client,
        "/v1/emails/?org=some-org",
        "get",
        {'Authorization': 'Bearer ' + USER_TOKEN}
    )
    assert response.status_code == 403


def test_get_emails_unauthenticated(app, client, mocker, domains_mock):
    response = client.get(
        "/v1/emails/?org=test-org",
    )
    assert response.status_code == 401


def test_get_emails_missing_org(app, client, mocker, domains_mock):
    response = client.get(
        "/v1/emails/",
        headers={'Authorization': 'Bearer ' + USER_TOKEN}
    )
    assert response.status_code == 400
