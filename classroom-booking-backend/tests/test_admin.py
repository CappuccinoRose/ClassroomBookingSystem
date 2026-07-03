import json
from datetime import date, timedelta


def create_classroom(client, admin_headers, room_no):
    resp = client.post('/api/classrooms', headers=admin_headers, json={
        'room_no': room_no, 'floor': 1, 'capacity': 50
    })
    return resp.get_json()['data']['classroom_id']


def test_admin_list_all_reservations(client, auth_headers, admin_headers):
    cid = create_classroom(client, admin_headers, 'A101')
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    # Create reservation as normal user
    client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': tomorrow,
        'start_time': '09:00',
        'end_time': '11:00',
        'purpose': 'User res'
    })
    # Admin should see it
    resp = client.get('/api/admin/reservations', headers=admin_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['code'] == 200
    assert len(data['data']['items']) >= 1


def test_admin_cancel_reservation(client, auth_headers, admin_headers):
    cid = create_classroom(client, admin_headers, 'A102')
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    create_resp = client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': tomorrow,
        'start_time': '09:00',
        'end_time': '11:00',
        'purpose': 'To be cancelled by admin'
    })
    rid = create_resp.get_json()['data']['reservation_id']
    resp = client.post(f'/api/admin/reservations/{rid}/cancel', headers=admin_headers)
    assert resp.status_code == 200
    # Verify
    get_resp = client.get(f'/api/reservations/{rid}', headers=auth_headers)
    assert get_resp.get_json()['data']['status'] == 0


def test_admin_access_denied_for_normal_user(client, auth_headers):
    resp = client.get('/api/admin/reservations', headers=auth_headers)
    assert resp.status_code == 403


def test_statistics(client, auth_headers, admin_headers):
    cid = create_classroom(client, admin_headers, 'A103')
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': tomorrow,
        'start_time': '09:00',
        'end_time': '11:00',
        'purpose': 'Stats test'
    })
    start = date.today().isoformat()
    end = (date.today() + timedelta(days=7)).isoformat()
    resp = client.get('/api/admin/statistics/usage', headers=admin_headers, query_string={
        'start_date': start,
        'end_date': end
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['code'] == 200
    assert 'usage' in data['data']
    assert 'hot_hours' in data['data']
