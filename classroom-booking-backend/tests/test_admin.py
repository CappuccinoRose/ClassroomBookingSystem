import pytest
from datetime import date, timedelta


def test_admin_list_all_reservations(client, admin_headers, sample_classroom):
    response = client.get('/api/admin/reservations', headers=admin_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200


def test_admin_cancel_reservation(client, admin_headers, auth_headers, sample_classroom):
    # Create reservation as normal user
    reserve_date = (date.today() + timedelta(days=1)).isoformat()
    response = client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': sample_classroom.classroom_id,
        'reserve_date': reserve_date,
        'start_time': '09:00',
        'end_time': '11:00',
        'purpose': '管理员取消测试'
    })
    reservation_id = response.get_json()['data']['reservation_id']

    # Admin cancels it
    response = client.post(f'/api/admin/reservations/{reservation_id}/cancel', headers=admin_headers)
    assert response.status_code == 200


def test_admin_forbidden_for_normal_user(client, auth_headers):
    response = client.get('/api/admin/reservations', headers=auth_headers)
    assert response.status_code == 403


def test_statistics(client, admin_headers):
    start = (date.today() - timedelta(days=30)).isoformat()
    end = date.today().isoformat()
    response = client.get('/api/admin/statistics/usage', headers=admin_headers, query_string={
        'start_date': start,
        'end_date': end
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['code'] == 200
    assert 'usage' in data['data']
