import ldap


def test_create_user(app, client, mocker):
    response = client.post(
        '/users/users/',
        json={
            'login': 'user1',
            'gn': 'Robert',
            'sn': 'Baran',
            'mail': 'rbaran@example.com',
            'password': 'baranek'})

    assert response.status_code == 201
    assert response.json == {
                            'login': 'user1',
                            'gn': 'Robert',
                            'sn': 'Baran',
                            'mail': 'rbaran@example.com',
                            'password': 'baranek'}
    app.DAO.ldap.add_s.assert_has_calls(
        [mocker.call(
            'cn=user1,ou=users,dc=example,dc=com',
            [
                ('objectClass', [b'inetOrgPerson']),
                ('cn', b'user1'),
                ('gn', b'Robert'),
                ('sn', b'Baran'),
                ('mail', b'rbaran@example.com'),
                ('userPassword', mocker.ANY),
            ]

        )],
        [mocker.call(
            'cn=user1,ou=groups,dc=example,dc=com',
            [
                ('objectClass', [b'groupOfNames']),
                ('cn', b'user1'),
                ('owner', b'cn=user1,ou=users,dc=example,dc=com'),
                ('member', [b'cn=user1,ou=users,dc=example,dc=com']),
            ]
        )]
        )


def test_create_user_wrong_input(client):
    response = client.post('/users/users/')
    assert response.status_code == 400


def test_duplicate_user(app, client, mocker):
    response = client.post('/users/users/', json={'login': 'user1',
                                                  'gn': 'Robert',
                                                  'sn': 'Baran',
                                                  'mail': 'rbaran@example.com',
                                                  'password': 'baranek'})

    assert response.status_code == 201
    mocker.patch.object(
        app.DAO.ldap,
        'add_s',
        side_effect=[ldap.ALREADY_EXISTS]
    )
    response = client.post('/users/users/', json={'login': 'user1',
                                                  'gn': 'Robert',
                                                  'sn': 'Baran',
                                                  'mail': 'rbaran@example.com',
                                                  'password': 'baranek'})

    assert response.status_code == 409


def test_create_user_get_405(client):
    response = client.get('/users/users/')
    assert response.status_code == 405


def test_duplicate_user_email(app, client, mocker):
    response = client.post('/users/users/', json={'login': 'user1',
                                                  'gn': 'Robert',
                                                  'sn': 'Baran',
                                                  'mail': 'rbaran@example.com',
                                                  'password': 'baranek'})

    assert response.status_code == 201
    mocker.patch.object(
        app.DAO.ldap,
        'add_s',
        side_effect=[ldap.ALREADY_EXISTS]
    )
    response = client.post('/users/users/', json={'login': 'user2',
                                                  'gn': 'Renata',
                                                  'sn': 'Baran',
                                                  'mail': 'rbaran@example.com',
                                                  'password': 'barankowa'})

    assert response.status_code == 409


def test_userinfo_noauth(client):
    response = client.get('/users/userinfo')
    assert response.status_code == 401


def test_userinfo_non_existing(app, client, mocker, domains_mock):
    mocker.patch.object(
        app.DAO.ldap,
        'search_s',
        return_value=[]
    )
    response = client.get(
        '/users/userinfo',
        headers={'Authorization': 'Bearer user1'}
    )
    assert response.status_code == 404


def test_userinfo(app, client, mocker, domains_mock):
    mocker.patch.object(
        app.DAO.ldap,
        'search_s',
        side_effect=[
            [[
                'cn=user1,ou=users,dc=example,dc=com',
                {
                    'objectClass': [b'inetOrgPerson'],
                    'cn': [b'user1'],
                    'givenName': [b'user1'],
                    'sn': [b'sn1'],
                    'mail': [b'mail1@mail.com'],
                }
            ]],
            [
                [
                    'cn=g1,ou=groups,dc=example,dc=com',
                    {
                        'objectClass': [b'groupOfNames'],
                        'cn':  [b'g1'],
                        'owner':  [b'cn=user1,ou=users,dc=example,dc=com'],
                        'member': [b'cn=user1,ou=users,dc=example,dc=com'],
                    }
                ],
                [
                    'cn=g2,ou=groups,dc=example,dc=com',
                    {
                        'objectClass': [b'groupOfNames'],
                        'cn':  [b'g2'],
                        'owner':  [b'cn=user1,ou=users,dc=example,dc=com'],
                        'member': [b'cn=user1,ou=users,dc=example,dc=com'],
                    }
                ],
            ]
        ])
    response = client.get(
        '/users/userinfo',
        headers={'Authorization': 'Bearer user1'}
    )
    assert response.status_code == 200
    assert response.json == {'username': 'user1',
                             'groups': ["g1", "g2"],
                             'sn': "sn1",
                             'gn': "user1",
                             'mail': "mail1@mail.com"}


def test_create_user_blacklist(app, client):
    response = client.post('/users/users/', json={'login': 'k8s-admins',
                                                  'gn': 'Robert',
                                                  'sn': 'Baran',
                                                  'mail': 'rbaran@example.com',
                                                  'password': 'baranek'})

    assert response.status_code == 403
