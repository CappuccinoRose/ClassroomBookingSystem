from datetime import datetime, date, timedelta
from app.models.periodic_rule import PeriodicRule
from app.models.reservation import Reservation
from app.extensions import db
from app.utils.conflict_check import check_conflict


def list_my_rules(user_id):
    return PeriodicRule.query.filter_by(user_id=user_id).order_by(PeriodicRule.create_time.desc()).all()


def create_rule(user_id, classroom_id, weekday, start_time, end_time, purpose,
                start_date, end_date):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%H:%M').time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, '%H:%M').time()

    if end_date <= start_date:
        return None, '规则结束日期必须晚于开始日期'

    if weekday < 1 or weekday > 7:
        return None, '星期参数错误'

    rule = PeriodicRule(
        user_id=user_id,
        classroom_id=classroom_id,
        weekday=weekday,
        start_time=start_time,
        end_time=end_time,
        purpose=purpose,
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(rule)
    db.session.commit()

    generate_reservations_for_rule(rule)

    return rule, None


def update_rule_status(rule_id, user_id, status):
    rule = PeriodicRule.query.filter_by(rule_id=rule_id, user_id=user_id).first()
    if not rule:
        return False, '规则不存在'
    rule.status = status
    db.session.commit()
    return True, None


def delete_rule(rule_id, user_id):
    rule = PeriodicRule.query.filter_by(rule_id=rule_id, user_id=user_id).first()
    if not rule:
        return False, '规则不存在'
    db.session.delete(rule)
    db.session.commit()
    return True, None


def generate_reservations_for_rule(rule, db_session=None):
    """为周期规则生成预订记录"""
    session = db_session or db.session
    today = date.today()
    current = max(rule.start_date, today)
    end = rule.end_date
    created = 0
    skipped = 0

    while current <= end:
        if current.isoweekday() == rule.weekday:
            if not check_conflict(rule.classroom_id, current, rule.start_time, rule.end_time):
                reservation = Reservation(
                    user_id=rule.user_id,
                    classroom_id=rule.classroom_id,
                    reserve_date=current,
                    start_time=rule.start_time,
                    end_time=rule.end_time,
                    purpose=rule.purpose,
                    status=2,
                    periodic_rule_id=rule.rule_id
                )
                session.add(reservation)
                created += 1
            else:
                skipped += 1
        current += timedelta(days=1)

    if db_session is None:
        session.commit()
    return created, skipped


def run_periodic_generation():
    """定时任务：为所有启用的周期规则生成未来预订"""
    rules = PeriodicRule.query.filter_by(status=1).all()
    for rule in rules:
        generate_reservations_for_rule(rule)
