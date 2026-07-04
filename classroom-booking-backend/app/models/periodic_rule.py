from app.extensions import db
from datetime import datetime, date


class PeriodicRule(db.Model):
    __tablename__ = 'periodic_rule'

    rule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('sys_user.user_id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.classroom_id'), nullable=False)
    weekday = db.Column(db.SmallInteger, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.SmallInteger, nullable=False, default=1)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self, include_classroom=False):
        data = {
            'rule_id': self.rule_id,
            'user_id': self.user_id,
            'classroom_id': self.classroom_id,
            'weekday': self.weekday,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'purpose': self.purpose,
            'start_date': self.start_date.isoformat() if isinstance(self.start_date, date) else self.start_date,
            'end_date': self.end_date.isoformat() if isinstance(self.end_date, date) else self.end_date,
            'status': self.status,
            'create_time': self.create_time.isoformat() if self.create_time else None
        }
        if include_classroom and self.classroom:
            data['classroom'] = self.classroom.to_dict()
        return data
