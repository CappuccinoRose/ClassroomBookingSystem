from app.models.classroom import Classroom
from app.models.reservation import Reservation
from app.extensions import db
from sqlalchemy import and_, or_
from datetime import datetime, time, date


def list_classrooms(page=1, per_page=10, floor=None, min_capacity=None, status=None):
    query = Classroom.query
    if floor is not None:
        query = query.filter(Classroom.floor == floor)
    if min_capacity is not None:
        query = query.filter(Classroom.capacity >= min_capacity)
    if status is not None:
        query = query.filter(Classroom.status == status)

    pagination = query.order_by(Classroom.room_no).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return pagination


def get_classroom(classroom_id):
    return Classroom.query.get(classroom_id)


def create_classroom(room_no, floor, capacity, has_projector=0, has_whiteboard=0, facility_remark=None):
    if Classroom.query.filter_by(room_no=room_no).first():
        return None, '教室编号已存在'

    classroom = Classroom(
        room_no=room_no,
        floor=floor,
        capacity=capacity,
        has_projector=has_projector,
        has_whiteboard=has_whiteboard,
        facility_remark=facility_remark
    )
    db.session.add(classroom)
    db.session.commit()
    return classroom, None


def update_classroom(classroom_id, **kwargs):
    classroom = Classroom.query.get(classroom_id)
    if not classroom:
        return None, '教室不存在'

    if 'room_no' in kwargs and kwargs['room_no'] != classroom.room_no:
        if Classroom.query.filter_by(room_no=kwargs['room_no']).first():
            return None, '教室编号已存在'

    for key, value in kwargs.items():
        if hasattr(classroom, key):
            setattr(classroom, key, value)

    db.session.commit()
    return classroom, None


def delete_classroom(classroom_id):
    classroom = Classroom.query.get(classroom_id)
    if not classroom:
        return False, '教室不存在'

    active_reservations = Reservation.query.filter(
        Reservation.classroom_id == classroom_id,
        Reservation.status.in_([1, 2]),
        Reservation.reserve_date >= date.today()
    ).count()

    if active_reservations > 0:
        return False, '该教室存在未来有效预订，无法删除'

    db.session.delete(classroom)
    db.session.commit()
    return True, None


def find_free_classrooms(reserve_date, start_time, end_time, min_capacity=None,
                         has_projector=None, has_whiteboard=None):
    """查询空闲教室"""
    query = Classroom.query.filter(Classroom.status == 1)

    if min_capacity is not None:
        query = query.filter(Classroom.capacity >= min_capacity)
    if has_projector is not None:
        query = query.filter(Classroom.has_projector == has_projector)
    if has_whiteboard is not None:
        query = query.filter(Classroom.has_whiteboard == has_whiteboard)

    classrooms = query.all()
    free_classrooms = []

    for classroom in classrooms:
        conflict = Reservation.query.filter(
            Reservation.classroom_id == classroom.classroom_id,
            Reservation.reserve_date == reserve_date,
            Reservation.status.in_([1, 2]),
            Reservation.start_time < end_time,
            Reservation.end_time > start_time
        ).first()

        if not conflict:
            free_classrooms.append(classroom)

    return free_classrooms
