from app.extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'sys_user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.SmallInteger, nullable=False, default=0)
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic')
    periodic_rules = db.relationship('PeriodicRule', backref='user', lazy='dynamic')
    approvals = db.relationship('Approval', backref='admin', lazy='dynamic', foreign_keys='Approval.admin_id')

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'status': self.status,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }
