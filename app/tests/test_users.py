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
    assert len(app.DAO.db) == 1
    u = app.DAO.db['cn=user1,ou=users,dc=example,dc=com']
    username = list(filter(lambda x: x[0] == "cn", u))[0][1]
    assert username == b"user1"
    email = list(filter(lambda x: x[0] == "mail", u))[0][1]
    assert email == b"rbaran@example.com"


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
