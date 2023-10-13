import ldap


def test_groups_create_single_org_no_auth(client):
    response = client.post(
        '/api/users/v1/users/groups/',
        json={'name': 'test_org'})
    assert response.status_code == 401


def test_groups_create_org_single_user(app, client, domains_mock):
    response = client.post(
        '/api/users/v1/users/groups/',
        json={'name': 'test_org'},
        headers={'Authorization': 'Bearer user1'})
    assert response.status_code == 201
    assert response.json == {'name': 'test_org',
                             'owner': 'test',
                             'members': ['test']}
    app.DAO.ldap.add_s.assert_called_once_with(
        'cn=test_org,ou=groups,dc=example,dc=com',
        [
            ('objectClass', [b'groupOfNames']),
            ('cn', b'test_org'),
            ('owner', b'cn=test,ou=users,dc=example,dc=com'),
            ('member', [
                b'cn=test,ou=users,dc=example,dc=com'
            ])
        ])


def test_groups_create_org_multi_user(app, client, domains_mock):
    response = client.post('/api/users/v1/users/groups/',
                           json={'name': 'test_org',
                                 'members': ['test_user2', 'test_user3']},
                           headers={'Authorization': 'Bearer user1'})
    assert response.status_code == 201
    assert response.json['name'] == 'test_org'
    assert response.json['owner'] == 'test'
    result_memebers = sorted(response.json['members'])
    expected_members_list = sorted(['test', 'test_user2', 'test_user3'])
    assert result_memebers == expected_members_list
    app.DAO.ldap.add_s.assert_called_once_with(
        'cn=test_org,ou=groups,dc=example,dc=com',
        [
            ('objectClass', [b'groupOfNames']),
            ('cn', b'test_org'),
            ('owner', b'cn=test,ou=users,dc=example,dc=com'),
            ('member', [
                b'cn=test_user2,ou=users,dc=example,dc=com',
                b'cn=test_user3,ou=users,dc=example,dc=com',
                b'cn=test,ou=users,dc=example,dc=com',
            ])
        ])


def test_groups_create_org_duplicate(app, client, mocker, domains_mock):
    mocker.patch.object(
        app.DAO.ldap,
        'add_s',
        side_effect=[None, ldap.ALREADY_EXISTS]
    )
    response = client.post('/api/users/v1/users/groups/',
                           json={'name': 'test_org'},
                           headers={'Authorization': 'Bearer user1'})
    assert response.status_code == 201
    response = client.post('/api/users/v1/users/groups/',
                           json={'name': 'test_org'},
                           headers={'Authorization': 'Bearer user1'})
    assert response.status_code == 409


def test_groups_create_org_blacklist(app, client, domains_mock):
    response = client.post('/api/users/v1/users/groups/',
                           json={'name': 'k8s-admins'},
                           headers={'Authorization': 'Bearer user1'})
    assert response.status_code == 403
