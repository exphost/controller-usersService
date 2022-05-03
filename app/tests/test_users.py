def test_create_user(app, client):
    response = client.post('/users/users/', json={'login': 'user1',
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
    assert len(app.DAO.users_db) == 1
    u = app.DAO.users_db['cn=user1,ou=users,dc=example,dc=com']
    username = list(filter(lambda x: x[0] == "cn", u))[0][1]
    assert username == b"user1"
    email = list(filter(lambda x: x[0] == "mail", u))[0][1]
    assert email == b"rbaran@example.com"

    # check the default group creation
    assert 'cn=user1,ou=groups,dc=example,dc=com' in app.DAO.groups_db
    g = app.DAO.groups_db['cn=user1,ou=groups,dc=example,dc=com']
    members = list(filter(lambda x: x[0] == "member", g))[0][1]
    assert len(members) == 1
    assert members == [b'cn=user1,ou=users,dc=example,dc=com', ]
    owner = list(filter(lambda x: x[0] == "owner", g))
    assert owner[0][1] == b'cn=user1,ou=users,dc=example,dc=com'


def test_create_user_wrong_input(client):
    response = client.post('/users/users/')
    assert response.status_code == 400


def test_duplicate_user(client):
    response = client.post('/users/users/', json={'login': 'user1',
                                                  'gn': 'Robert',
                                                  'sn': 'Baran',
                                                  'mail': 'rbaran@example.com',
                                                  'password': 'baranek'})

    assert response.status_code == 201
    response = client.post('/users/users/', json={'login': 'user1',
                                                  'gn': 'Robert',
                                                  'sn': 'Baran',
                                                  'mail': 'rbaran@example.com',
                                                  'password': 'baranek'})

    assert response.status_code == 409


def test_create_user_get_405(client):
    response = client.get('/users/users/')
    assert response.status_code == 405


def test_duplicate_user_email(client):
    response = client.post('/users/users/', json={'login': 'user1',
                                                  'gn': 'Robert',
                                                  'sn': 'Baran',
                                                  'mail': 'rbaran@example.com',
                                                  'password': 'baranek'})

    assert response.status_code == 201
    response = client.post('/users/users/', json={'login': 'user2',
                                                  'gn': 'Renata',
                                                  'sn': 'Baran',
                                                  'mail': 'rbaran@example.com',
                                                  'password': 'barankowa'})

    assert response.status_code == 409


def test_userinfo_noauth(client):
    response = client.get('/users/userinfo')
    assert response.status_code == 401


def test_userinfo_non_existing(app, client):
    app.DAO.create_user("user1", "user1", "sn1", "mail1@mail.com", "pass1")
    app.DAO.create_user("user2", "user2", "sn2", "mail2@mail.com", "pass2")
    app.DAO.create_group("g1", "user1", ["user1", ])
    app.DAO.create_group("g2", "user1", ["user1", "user2"])
    app.DAO.create_group("g3", "user2", ["user2", ])
    app.DAO.create_group("g4", "user2", ["user2", "user1"])
    response = client.get('/users/userinfo',
                          headers={'X-User': 'user3'})
    assert response.status_code == 404


def test_userinfo(app, client):
    app.DAO.create_user("user1", "user1", "sn1", "mail1@mail.com", "pass1")
    app.DAO.create_user("user2", "user2", "sn2", "mail2@mail.com", "pass2")
    app.DAO.create_group("g1", "user1", ["user1", ])
    app.DAO.create_group("g2", "user1", ["user1", "user2"])
    app.DAO.create_group("g3", "user2", ["user2", ])
    app.DAO.create_group("g4", "user2", ["user2", "user1"])
    response = client.get('/users/userinfo',
                          headers={'X-User': 'user1'})
    assert response.status_code == 200
    assert response.json == {'username': 'user1',
                             'groups': ["g1", "g2", "g4"],
                             'sn': "sn1",
                             'gn': "user1",
                             'mail': "mail1@mail.com"}
