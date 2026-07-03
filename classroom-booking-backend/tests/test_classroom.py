import json


def test_list_classrooms(client, auth_headers):
    resp = client.get('/api/classrooms', headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['code'] == 200
    assert 'items' in data['data']


def test_create_classroom_admin(client, admin_headers):
    resp = client.post('/api/classrooms', headers=admin_headers, json={
        'room_no': '201',
        'floor': 2,
        'capacity': 60,
        'has_projector': 1,
        'has_whiteboard': 0
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['code'] == 200
    assert data['data']['room_no'] == '201'


def test_create_classroom_normal_user_forbidden(client, auth_headers):
    resp = client.post('/api/classrooms', headers=auth_headers, json={
        'room_no': '202',
        'floor': 2,
        'capacity': 60
    })
    assert resp.status_code == 403


def test_create_classroom_duplicate_room_no(client, admin_headers):
    client.post('/api/classrooms', headers=admin_headers, json={
        'room_no': '301',
        'floor': 3,
        'capacity': 40
    })
    resp = client.post('/api/classrooms', headers=admin_headers, json={
        'room_no': '301',
        'floor': 3,
        'capacity': 50
    })
    assert resp.status_code == 400
    assert resp.get_json()['code'] == 400


def test_get_classroom(client, auth_headers, admin_headers):
    create_resp = client.post('/api/classrooms', headers=admin_headers, json={
        'room_no': '401',
        'floor': 4,
        'capacity': 30
    })
    classroom_id = create_resp.get_json()['data']['classroom_id']
    resp = client.get(f'/api/classrooms/{classroom_id}', headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['data']['room_no'] == '401'


def test_update_classroom(client, admin_headers):
    create_resp = client.post('/api/classrooms', headers=admin_headers, json={
        'room_no': '501',
        'floor': 5,
        'capacity': 20
    })
    classroom_id = create_resp.get_json()['data']['classroom_id']
    resp = client.put(f'/api/classrooms/{classroom_id}', headers=admin_headers, json={
        'capacity': 100
    })
    assert resp.status_code == 200
    assert resp.get_json()['data']['capacity'] == 100


def test_delete_classroom(client, admin_headers):
    create_resp = client.post('/api/classrooms', headers=admin_headers, json={
        'room_no': '601',
        'floor': 6,
        'capacity': 15
    })
    classroom_id = create_resp.get_json()['data']['classroom_id']
    resp = client.delete(f'/api/classrooms/{classroom_id}', headers=admin_headers)
    assert resp.status_code == 200
    # Verify deleted
    resp2 = client.get(f'/api/classrooms/{classroom_id}', headers=admin_headers)
    assert resp2.status_code == 404


def test_find_free_classrooms(client, auth_headers, admin_headers):
    # Create classroom
    client.post('/api/classrooms', headers=admin_headers, json={
        'room_no': '701',
        'floor': 7,
        'capacity': 40
    })
    from datetime import date
    resp = client.get('/api/classrooms/free', headers=auth_headers, query_string={
        'reserve_date': date.today().isoformat(),
        'start_time': '09:00',
        'end_time': '11:00'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['code'] == 200
    assert isinstance(data['data'], list)
