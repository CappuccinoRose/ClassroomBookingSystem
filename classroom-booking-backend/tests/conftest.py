import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.classroom import Classroom
import bcrypt


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
def auth_headers(client):
    """Create a test user and return auth headers"""
    # Register user
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'password': 'password123',
        'email': 'test@example.com'
    })

    # Login
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    token = response.get_json()['data']['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_headers(client):
    """Create a test admin and return auth headers"""
    # Create admin directly
    from app.extensions import db
    admin = User(
        username='admin',
        password_hash=bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        email='admin@example.com',
        role=1,
        status=1
    )
    db.session.add(admin)
    db.session.commit()

    # Login
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    token = response.get_json()['data']['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_classroom(app):
    classroom = Classroom(
        room_no='101',
        floor=1,
        capacity=30,
        has_projector=1,
        has_whiteboard=1,
        status=1
    )
    db.session.add(classroom)
    db.session.commit()
    return classroom
