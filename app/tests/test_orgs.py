def test_groups_create_single_org_no_auth(client):
    response = client.post('/users/groups/', json={'name': 'test_org'})
    assert response.status_code == 401


def test_groups_create_org_single_user(app, client):
    response = client.post('/users/groups/',
                           json={'name': 'test_org'},
                           headers={'X-User': 'test_user'})
    assert response.status_code == 201
    assert response.json == {'name': 'test_org',
                             'owner': 'test_user',
                             'members': ['test_user']}
    assert len(app.DAO.groups_db) == 1
    u = app.DAO.groups_db['cn=test_org,ou=groups,dc=example,dc=com']
    cn = list(filter(lambda x: x[0] == "cn", u))[0][1]
    assert cn == b"test_org"
    owner = list(filter(lambda x: x[0] == "owner", u))[0][1]
    assert owner == b"cn=test_user,ou=users,dc=example,dc=com"
    members = list(filter(lambda x: x[0] == "member", u))
    assert members[0][1] == [b"cn=test_user,ou=users,dc=example,dc=com"]


def test_groups_create_org_multi_user(app, client):
    response = client.post('/users/groups/',
                           json={'name': 'test_org',
                                 'members': ['test_user2', 'test_user3']},
                           headers={'X-User': 'test_user'})
    assert response.status_code == 201
    assert response.json['name'] == 'test_org'
    assert response.json['owner'] == 'test_user'
    result_memebers = sorted(response.json['members'])
    expected_members_list = sorted(['test_user', 'test_user2', 'test_user3'])
    assert result_memebers == expected_members_list

    assert len(app.DAO.groups_db) == 1
    u = app.DAO.groups_db['cn=test_org,ou=groups,dc=example,dc=com']
    cn = list(filter(lambda x: x[0] == "cn", u))[0][1]
    assert cn == b"test_org"
    owner = list(filter(lambda x: x[0] == "owner", u))[0][1]
    assert owner == b"cn=test_user,ou=users,dc=example,dc=com"
    members = sorted(list(filter(lambda x: x[0] == "member", u))[0][1])
    expected_members = sorted([b"cn=test_user,ou=users,dc=example,dc=com",
                               b"cn=test_user2,ou=users,dc=example,dc=com",
                               b"cn=test_user3,ou=users,dc=example,dc=com"])
    assert members == expected_members


def test_groups_create_org_duplicate(app, client):
    response = client.post('/users/groups/',
                           json={'name': 'test_org'},
                           headers={'X-User': 'test_user'})
    assert response.status_code == 201
    response = client.post('/users/groups/',
                           json={'name': 'test_org'},
                           headers={'X-User': 'test_user'})
    assert response.status_code == 409


def test_groups_create_org_blacklist(app, client):
    response = client.post('/users/groups/',
                           json={'name': 'k8s-admins'},
                           headers={'X-User': 'test_user'})
    assert response.status_code == 403
