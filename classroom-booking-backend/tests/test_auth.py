import pytest


def test_register(client):
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'password': 'password123',
        'email': 'new@example.com'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert data['data']['username'] == 'newuser'


def test_register_duplicate_username(client):
    client.post('/api/auth/register', json={
        'username': 'dupuser',
        'password': 'password123',
        'email': 'dup@example.com'
    })
    response = client.post('/api/auth/register', json={
        'username': 'dupuser',
        'password': 'password123',
        'email': 'dup2@example.com'
    })
    assert response.status_code == 400


def test_login(client):
    client.post('/api/auth/register', json={
        'username': 'loguser',
        'password': 'password123',
        'email': 'log@example.com'
    })
    response = client.post('/api/auth/login', json={
        'username': 'loguser',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert 'token' in data['data']


def test_login_wrong_password(client):
    client.post('/api/auth/register', json={
        'username': 'wronguser',
        'password': 'password123',
        'email': 'wrong@example.com'
    })
    response = client.post('/api/auth/login', json={
        'username': 'wronguser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 400


def test_get_userinfo(client, auth_headers):
    response = client.get('/api/auth/userinfo', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert data['data']['username'] == 'testuser'


def test_change_password(client, auth_headers):
    response = client.put('/api/auth/password', headers=auth_headers, json={
        'old_password': 'password123',
        'new_password': 'newpassword456'
    })
    assert response.status_code == 200

    # Login with new password
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'newpassword456'
    })
    assert response.status_code == 200
