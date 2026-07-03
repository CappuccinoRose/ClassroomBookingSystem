from app.extensions import db
from datetime import datetime


class Classroom(db.Model):
    __tablename__ = 'classroom'

    classroom_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_no = db.Column(db.String(50), unique=True, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    has_projector = db.Column(db.SmallInteger, nullable=False, default=0)
    has_whiteboard = db.Column(db.SmallInteger, nullable=False, default=0)
    facility_remark = db.Column(db.String(255), nullable=True)
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reservations = db.relationship('Reservation', backref='classroom', lazy='dynamic')
    periodic_rules = db.relationship('PeriodicRule', backref='classroom', lazy='dynamic')

    def to_dict(self):
        return {
            'classroom_id': self.classroom_id,
            'room_no': self.room_no,
            'floor': self.floor,
            'capacity': self.capacity,
            'has_projector': self.has_projector,
            'has_whiteboard': self.has_whiteboard,
            'facility_remark': self.facility_remark,
            'status': self.status,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }
