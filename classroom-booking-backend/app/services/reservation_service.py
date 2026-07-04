from datetime import datetime, date, timedelta
from app.models.reservation import Reservation
from app.models.classroom import Classroom
from app.models.user import User
from app.extensions import db
from app.utils.conflict_check import check_conflict


def list_my_reservations(user_id, page=1, per_page=10, status=None):
    query = Reservation.query.filter_by(user_id=user_id)
    if status is not None:
        query = query.filter(Reservation.status == status)
    return query.order_by(Reservation.create_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )


def get_reservation(reservation_id, user_id=None):
    query = Reservation.query.filter_by(reservation_id=reservation_id)
    if user_id is not None:
        query = query.filter_by(user_id=user_id)
    return query.first()


def create_reservation(user_id, classroom_id, reserve_date, start_time, end_time, purpose,
                       periodic_rule_id=None, is_admin=False):
    if isinstance(reserve_date, str):
        reserve_date = datetime.strptime(reserve_date, '%Y-%m-%d').date()
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%H:%M').time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, '%H:%M').time()

    classroom = Classroom.query.get(classroom_id)
    if not classroom:
        return None, '教室不存在'
    if classroom.status == 0:
        return None, '教室已停用'

    if end_time <= start_time:
        return None, '结束时间必须晚于开始时间'

    if reserve_date < date.today():
        return None, '不能预订过去的日期'

    if check_conflict(classroom_id, reserve_date, start_time, end_time):
        return None, '该时段已被预订，请选择其他时段'

    status = 2 if is_admin else 2

    reservation = Reservation(
        user_id=user_id,
        classroom_id=classroom_id,
        reserve_date=reserve_date,
        start_time=start_time,
        end_time=end_time,
        purpose=purpose,
        status=status,
        periodic_rule_id=periodic_rule_id
    )
    db.session.add(reservation)
    db.session.commit()
    return reservation, None


def update_reservation(reservation_id, user_id, **kwargs):
    reservation = Reservation.query.filter_by(
        reservation_id=reservation_id, user_id=user_id
    ).first()
    if not reservation:
        return None, '预订不存在'
    if reservation.status in [0, 3, 4]:
        return None, '该预订状态不允许修改'

    reserve_date = kwargs.get('reserve_date', reservation.reserve_date)
    start_time = kwargs.get('start_time', reservation.start_time)
    end_time = kwargs.get('end_time', reservation.end_time)
    classroom_id = kwargs.get('classroom_id', reservation.classroom_id)

    if isinstance(reserve_date, str):
        reserve_date = datetime.strptime(reserve_date, '%Y-%m-%d').date()
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%H:%M').time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, '%H:%M').time()

    if end_time <= start_time:
        return None, '结束时间必须晚于开始时间'

    if reserve_date < date.today():
        return None, '不能修改为过去的日期'

    if check_conflict(classroom_id, reserve_date, start_time, end_time, exclude_id=reservation_id):
        return None, '修改后的时段存在冲突'

    reservation.reserve_date = reserve_date
    reservation.start_time = start_time
    reservation.end_time = end_time
    reservation.classroom_id = classroom_id
    if 'purpose' in kwargs:
        reservation.purpose = kwargs['purpose']

    db.session.commit()
    return reservation, None


def cancel_reservation(reservation_id, user_id, is_admin=False):
    reservation = Reservation.query.filter_by(
        reservation_id=reservation_id, user_id=user_id
    ).first() if not is_admin else Reservation.query.get(reservation_id)

    if not reservation:
        return False, '预订不存在'
    if reservation.status == 0:
        return False, '预订已取消'

    if not is_admin:
        now = datetime.now()
        start_datetime = datetime.combine(reservation.reserve_date, reservation.start_time)
        if (start_datetime - now).total_seconds() < 40 * 60:
            return False, '距预订开始不足40分钟，无法自主取消，请联系管理员'

    reservation.status = 0
    db.session.commit()
    return True, None


def list_all_reservations(page=1, per_page=10, status=None, classroom_id=None,
                          start_date=None, end_date=None, username=None, room_no=None):
    query = Reservation.query
    if status is not None:
        query = query.filter(Reservation.status == status)
    if classroom_id is not None:
        query = query.filter(Reservation.classroom_id == classroom_id)
    if start_date is not None:
        query = query.filter(Reservation.reserve_date >= start_date)
    if end_date is not None:
        query = query.filter(Reservation.reserve_date <= end_date)
    if username:
        query = query.join(User).filter(User.username.ilike(f'%{username}%'))
    if room_no:
        query = query.join(Classroom).filter(Classroom.room_no.ilike(f'%{room_no}%'))

    return query.order_by(Reservation.create_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )


def admin_cancel_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return False, '预订不存在'
    if reservation.status == 0:
        return False, '预订已取消'

    reservation.status = 0
    db.session.commit()
    return True, None


def restore_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return False, '预订不存在'
    if reservation.status != 0:
        return False, '只有已取消的预订可以恢复'

    # 恢复为已确认状态
    reservation.status = 2
    db.session.commit()
    return True, None
