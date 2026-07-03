from app.extensions import db
from datetime import datetime, date, time


class Reservation(db.Model):
    __tablename__ = 'reservation'

    reservation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('sys_user.user_id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.classroom_id'), nullable=False)
    reserve_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    status = db.Column(db.SmallInteger, nullable=False, default=2)
    periodic_rule_id = db.Column(db.Integer, db.ForeignKey('periodic_rule.rule_id'), nullable=True)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    approval = db.relationship('Approval', backref='reservation', uselist=False, lazy='joined')
    periodic_rule = db.relationship('PeriodicRule', backref='reservations', lazy='joined')

    def to_dict(self, include_user=False, include_classroom=False):
        data = {
            'reservation_id': self.reservation_id,
            'user_id': self.user_id,
            'classroom_id': self.classroom_id,
            'reserve_date': self.reserve_date.isoformat() if isinstance(self.reserve_date, date) else self.reserve_date,
            'start_time': self.start_time.isoformat() if isinstance(self.start_time, time) else self.start_time,
            'end_time': self.end_time.isoformat() if isinstance(self.end_time, time) else self.end_time,
            'purpose': self.purpose,
            'status': self.status,
            'periodic_rule_id': self.periodic_rule_id,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }
        if include_user and self.user:
            data['user'] = self.user.to_dict()
        if include_classroom and self.classroom:
            data['classroom'] = self.classroom.to_dict()
        if self.approval:
            data['approval'] = self.approval.to_dict()
        return data
