import os
import pytest

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'
os.environ['SECRET_KEY'] = 'test-secret'

from app import create_app
from app.extensions import db
from app.models import User, Classroom, Reservation, Approval, PeriodicRule


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-jwt-secret',
        'SECRET_KEY': 'test-secret'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Create a normal user and return auth headers."""
    with app.app_context():
        from app.services.auth_service import register_user
        user, _ = register_user('testuser', 'password123', 'test@example.com')
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user.user_id))
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


@pytest.fixture
def admin_headers(app):
    """Create an admin user and return auth headers."""
    with app.app_context():
        from app.services.auth_service import register_user
        user, _ = register_user('adminuser', 'password123', 'admin@example.com')
        user.role = 1
        db.session.commit()
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(user.user_id))
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


@pytest.fixture
def sample_classroom(app):
    with app.app_context():
        classroom = Classroom(
            room_no='101',
            floor=1,
            capacity=50,
            has_projector=1,
            has_whiteboard=1,
            status=1
        )
        db.session.add(classroom)
        db.session.commit()
        return classroom.classroom_id


@pytest.fixture
def sample_reservation(app, auth_headers, sample_classroom):
    with app.app_context():
        from app.services.reservation_service import create_reservation
        from datetime import date, time
        user_id = int(auth_headers['Authorization'].split(' ')[1])  # This won't work directly
        # We need to get user from token; simplified: create reservation manually
        from flask_jwt_extended import decode_token
        # Actually let's just create it directly
        from app.models.user import User
        user = User.query.filter_by(username='testuser').first()
        reservation = Reservation(
            user_id=user.user_id,
            classroom_id=sample_classroom,
            reserve_date=date(2025, 12, 31),
            start_time=time(9, 0),
            end_time=time(11, 0),
            purpose='Test meeting',
            status=2
        )
        db.session.add(reservation)
        db.session.commit()
        return reservation.reservation_id
