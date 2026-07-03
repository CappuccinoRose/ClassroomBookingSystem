import json
from datetime import date, time, timedelta, datetime


def create_classroom(client, admin_headers, room_no):
    resp = client.post('/api/classrooms', headers=admin_headers, json={
        'room_no': room_no, 'floor': 1, 'capacity': 50
    })
    return resp.get_json()['data']['classroom_id']


def test_create_reservation_success(client, auth_headers, admin_headers):
    cid = create_classroom(client, admin_headers, 'R101')
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    resp = client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': tomorrow,
        'start_time': '09:00',
        'end_time': '11:00',
        'purpose': 'Team meeting'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['code'] == 200
    assert data['data']['purpose'] == 'Team meeting'


def test_create_reservation_conflict(client, auth_headers, admin_headers):
    cid = create_classroom(client, admin_headers, 'R102')
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    # First reservation
    client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': tomorrow,
        'start_time': '09:00',
        'end_time': '11:00',
        'purpose': 'First'
    })
    # Second overlapping reservation
    resp = client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': tomorrow,
        'start_time': '10:00',
        'end_time': '12:00',
        'purpose': 'Second'
    })
    assert resp.status_code == 409
    assert resp.get_json()['code'] == 409


def test_create_reservation_past_date(client, auth_headers, admin_headers):
    cid = create_classroom(client, admin_headers, 'R103')
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    resp = client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': yesterday,
        'start_time': '09:00',
        'end_time': '11:00',
        'purpose': 'Past'
    })
    assert resp.status_code == 409


def test_create_reservation_invalid_time(client, auth_headers, admin_headers):
    cid = create_classroom(client, admin_headers, 'R104')
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    resp = client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': tomorrow,
        'start_time': '14:00',
        'end_time': '12:00',
        'purpose': 'Invalid'
    })
    assert resp.status_code == 409


def test_list_my_reservations(client, auth_headers, admin_headers):
    cid = create_classroom(client, admin_headers, 'R105')
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': tomorrow,
        'start_time': '09:00',
        'end_time': '11:00',
        'purpose': 'My reservation'
    })
    resp = client.get('/api/reservations/my', headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['code'] == 200
    assert len(data['data']['items']) >= 1


def test_cancel_reservation_success(client, auth_headers, admin_headers):
    cid = create_classroom(client, admin_headers, 'R106')
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    create_resp = client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': tomorrow,
        'start_time': '09:00',
        'end_time': '11:00',
        'purpose': 'To cancel'
    })
    rid = create_resp.get_json()['data']['reservation_id']
    resp = client.post(f'/api/reservations/{rid}/cancel', headers=auth_headers)
    assert resp.status_code == 200
    # Verify status
    get_resp = client.get(f'/api/reservations/{rid}', headers=auth_headers)
    assert get_resp.get_json()['data']['status'] == 0


def test_cancel_reservation_too_late(client, auth_headers, admin_headers, app):
    # Create a reservation for today but in the future (more than 40 min)
    cid = create_classroom(client, admin_headers, 'R107')
    # We'll create directly in DB for a reservation starting soon
    with app.app_context():
        from app.extensions import db
        from app.models.reservation import Reservation
        from app.models.user import User
        user = User.query.filter_by(username='testuser').first()
        now = datetime.now()
        start = (now + timedelta(minutes=20)).time()  # Only 20 min away
        end = (now + timedelta(minutes=80)).time()
        reservation = Reservation(
            user_id=user.user_id,
            classroom_id=cid,
            reserve_date=date.today(),
            start_time=start,
            end_time=end,
            purpose='Soon',
            status=2
        )
        db.session.add(reservation)
        db.session.commit()
        rid = reservation.reservation_id

    resp = client.post(f'/api/reservations/{rid}/cancel', headers=auth_headers)
    assert resp.status_code == 400
    assert '40分钟' in resp.get_json()['message']


def test_update_reservation(client, auth_headers, admin_headers):
    cid = create_classroom(client, admin_headers, 'R108')
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    create_resp = client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': tomorrow,
        'start_time': '09:00',
        'end_time': '11:00',
        'purpose': 'Original'
    })
    rid = create_resp.get_json()['data']['reservation_id']
    resp = client.put(f'/api/reservations/{rid}', headers=auth_headers, json={
        'purpose': 'Updated purpose'
    })
    assert resp.status_code == 200
    assert resp.get_json()['data']['purpose'] == 'Updated purpose'


def test_update_reservation_conflict(client, auth_headers, admin_headers):
    cid = create_classroom(client, admin_headers, 'R109')
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    # First reservation 9-11
    client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': tomorrow,
        'start_time': '09:00',
        'end_time': '11:00',
        'purpose': 'First'
    })
    # Second reservation 13-15
    create_resp = client.post('/api/reservations', headers=auth_headers, json={
        'classroom_id': cid,
        'reserve_date': tomorrow,
        'start_time': '13:00',
        'end_time': '15:00',
        'purpose': 'Second'
    })
    rid = create_resp.get_json()['data']['reservation_id']
    # Try to update second to 10-12 (conflicts with first)
    resp = client.put(f'/api/reservations/{rid}', headers=auth_headers, json={
        'start_time': '10:00',
        'end_time': '12:00'
    })
    assert resp.status_code == 409


def test_periodic_rule_create(client, auth_headers, admin_headers):
    cid = create_classroom(client, admin_headers, 'R110')
    start = (date.today() + timedelta(days=1)).isoformat()
    end = (date.today() + timedelta(days=30)).isoformat()
    resp = client.post('/api/reservations/periodic-rules', headers=auth_headers, json={
        'classroom_id': cid,
        'weekday': 1,
        'start_time': '14:00',
        'end_time': '16:00',
        'purpose': 'Weekly meeting',
        'start_date': start,
        'end_date': end
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['code'] == 200
