from datetime import datetime, date, timedelta
from sqlalchemy import func, extract
from app.models.reservation import Reservation
from app.models.classroom import Classroom
from app.extensions import db


def get_usage_statistics(start_date, end_date, group_by='classroom'):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    reservations = Reservation.query.filter(
        Reservation.reserve_date >= start_date,
        Reservation.reserve_date <= end_date,
        Reservation.status == 2
    ).all()

    classroom_stats = {}
    for r in reservations:
        cid = r.classroom_id
        start_dt = datetime.combine(r.reserve_date, r.start_time)
        end_dt = datetime.combine(r.reserve_date, r.end_time)
        minutes = int((end_dt - start_dt).total_seconds() / 60)
        if cid not in classroom_stats:
            classroom_stats[cid] = {'count': 0, 'minutes': 0}
        classroom_stats[cid]['count'] += 1
        classroom_stats[cid]['minutes'] += minutes

    results = []
    total_days = (end_date - start_date).days + 1
    total_available_minutes = total_days * 12 * 60

    for cid, stats in classroom_stats.items():
        classroom = Classroom.query.get(cid)
        if not classroom:
            continue
        total_minutes = stats['minutes']
        usage_rate = round((total_minutes / total_available_minutes) * 100, 2) if total_available_minutes > 0 else 0

        results.append({
            'classroom_id': cid,
            'room_no': classroom.room_no,
            'floor': classroom.floor,
            'capacity': classroom.capacity,
            'reservation_count': stats['count'],
            'total_hours': round(total_minutes / 60, 2),
            'usage_rate': usage_rate
        })

    return results


def get_hot_hours(start_date, end_date):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    query = db.session.query(
        extract('hour', Reservation.start_time).label('hour'),
        func.count(Reservation.reservation_id).label('count')
    ).filter(
        Reservation.reserve_date >= start_date,
        Reservation.reserve_date <= end_date,
        Reservation.status == 2
    ).group_by(extract('hour', Reservation.start_time)).order_by('hour')

    results = []
    for row in query.all():
        results.append({
            'hour': int(row.hour),
            'count': row.count
        })

    return results
