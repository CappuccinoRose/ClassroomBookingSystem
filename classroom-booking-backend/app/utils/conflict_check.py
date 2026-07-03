from app.models.reservation import Reservation
from app.extensions import db


def check_conflict(classroom_id, reserve_date, start_time, end_time, exclude_id=None):
    """
    检查指定教室在指定日期和时间段是否存在冲突预订

    冲突状态：待审核(1)、已确认(2)
    排除状态：已取消(0)、已驳回(3)、已完成(4)
    """
    query = Reservation.query.filter(
        Reservation.classroom_id == classroom_id,
        Reservation.reserve_date == reserve_date,
        Reservation.status.in_([1, 2]),
        Reservation.start_time < end_time,
        Reservation.end_time > start_time
    )

    if exclude_id is not None:
        query = query.filter(Reservation.reservation_id != exclude_id)

    return query.first() is not None


def get_conflicting_reservations(classroom_id, reserve_date, start_time, end_time, exclude_id=None):
    """获取与指定时段冲突的所有预订记录"""
    query = Reservation.query.filter(
        Reservation.classroom_id == classroom_id,
        Reservation.reserve_date == reserve_date,
        Reservation.status.in_([1, 2]),
        Reservation.start_time < end_time,
        Reservation.end_time > start_time
    )

    if exclude_id is not None:
        query = query.filter(Reservation.reservation_id != exclude_id)

    return query.all()
