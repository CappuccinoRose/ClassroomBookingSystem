from app.models.approval import Approval
from app.models.reservation import Reservation
from app.extensions import db
from app.utils.conflict_check import check_conflict


def list_pending_approvals(page=1, per_page=10):
    query = Reservation.query.filter_by(status=1).order_by(Reservation.create_time.desc())
    return query.paginate(page=page, per_page=per_page, error_out=False)


def approve_reservation(reservation_id, admin_id, result, opinion=None):
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return None, '预订不存在'
    if reservation.status != 1:
        return None, '该预订不处于待审核状态'

    if result == 1:
        if check_conflict(reservation.classroom_id, reservation.reserve_date,
                          reservation.start_time, reservation.end_time,
                          exclude_id=reservation.reservation_id):
            return None, '审核期间该时段已被占用，无法通过'
        reservation.status = 2
    else:
        reservation.status = 3

    approval = Approval(
        reservation_id=reservation_id,
        admin_id=admin_id,
        result=result,
        opinion=opinion
    )
    db.session.add(approval)
    db.session.commit()
    return approval, None
