import pytest
from datetime import date, time


def test_list_classrooms(client, auth_headers):
    response = client.get('/api/classrooms', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200


def test_create_classroom_admin(client, admin_headers):
    response = client.post('/api/classrooms', headers=admin_headers, json={
        'room_no': '301',
        'floor': 3,
        'capacity': 50,
        'has_projector': 1,
        'has_whiteboard': 0
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert data['data']['room_no'] == '301'


def test_create_classroom_forbidden(client, auth_headers):
    response = client.post('/api/classrooms', headers=auth_headers, json={
        'room_no': '302',
        'floor': 3,
        'capacity': 50
    })
    assert response.status_code == 403


def test_update_classroom(client, admin_headers, sample_classroom):
    response = client.put(f'/api/classrooms/{sample_classroom.classroom_id}', headers=admin_headers, json={
        'capacity': 50
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['data']['capacity'] == 50


def test_delete_classroom(client, admin_headers, sample_classroom):
    response = client.delete(f'/api/classrooms/{sample_classroom.classroom_id}', headers=admin_headers)
    assert response.status_code == 200


def test_find_free_classrooms(client, auth_headers, sample_classroom):
    response = client.get('/api/classrooms/free', headers=auth_headers, query_string={
        'reserve_date': '2026-01-01',
        'start_time': '09:00',
        'end_time': '11:00'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
