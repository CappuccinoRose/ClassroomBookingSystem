import json


def test_register_success(client):
    resp = client.post('/api/auth/register', json={
        'username': 'newuser',
        'password': 'password123',
        'email': 'new@example.com'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['code'] == 200
    assert data['data']['username'] == 'newuser'


def test_register_duplicate_username(client):
    client.post('/api/auth/register', json={
        'username': 'dupuser',
        'password': 'password123',
        'email': 'dup1@example.com'
    })
    resp = client.post('/api/auth/register', json={
        'username': 'dupuser',
        'password': 'password123',
        'email': 'dup2@example.com'
    })
    assert resp.status_code == 400
    assert resp.get_json()['code'] == 400


def test_register_duplicate_email(client):
    client.post('/api/auth/register', json={
        'username': 'user1',
        'password': 'password123',
        'email': 'same@example.com'
    })
    resp = client.post('/api/auth/register', json={
        'username': 'user2',
        'password': 'password123',
        'email': 'same@example.com'
    })
    assert resp.status_code == 400


def test_login_success(client):
    client.post('/api/auth/register', json={
        'username': 'loguser',
        'password': 'password123',
        'email': 'log@example.com'
    })
    resp = client.post('/api/auth/login', json={
        'username': 'loguser',
        'password': 'password123'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['code'] == 200
    assert 'token' in data['data']


def test_login_wrong_password(client):
    client.post('/api/auth/register', json={
        'username': 'loguser2',
        'password': 'password123',
        'email': 'log2@example.com'
    })
    resp = client.post('/api/auth/login', json={
        'username': 'loguser2',
        'password': 'wrongpassword'
    })
    assert resp.status_code == 400


def test_userinfo(client, auth_headers):
    resp = client.get('/api/auth/userinfo', headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['code'] == 200
    assert data['data']['username'] == 'testuser'


def test_userinfo_no_token(client):
    resp = client.get('/api/auth/userinfo')
    assert resp.status_code == 401


def test_change_password(client, auth_headers):
    resp = client.put('/api/auth/password', headers=auth_headers, json={
        'old_password': 'password123',
        'new_password': 'newpassword456'
    })
    assert resp.status_code == 200
    # Login with new password
    resp2 = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'newpassword456'
    })
    assert resp2.status_code == 200


def test_change_password_wrong_old(client, auth_headers):
    resp = client.put('/api/auth/password', headers=auth_headers, json={
        'old_password': 'wrongold',
        'new_password': 'newpassword456'
    })
    assert resp.status_code == 400
