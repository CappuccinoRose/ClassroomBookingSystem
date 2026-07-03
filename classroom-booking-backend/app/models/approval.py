from app.extensions import db
from datetime import datetime


class Approval(db.Model):
    __tablename__ = 'approval'

    approval_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.reservation_id'), unique=True, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('sys_user.user_id'), nullable=False)
    result = db.Column(db.SmallInteger, nullable=False)
    opinion = db.Column(db.String(255), nullable=True)
    approval_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'approval_id': self.approval_id,
            'reservation_id': self.reservation_id,
            'admin_id': self.admin_id,
            'result': self.result,
            'opinion': self.opinion,
            'approval_time': self.approval_time.isoformat() if self.approval_time else None
        }
