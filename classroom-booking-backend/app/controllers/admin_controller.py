from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services import reservation_service, approval_service, statistics_service
from app.schemas.reservation_schema import ApprovalSchema
from app.utils.response import success, error, not_found
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

approval_schema = ApprovalSchema()


# Admin reservations
@admin_bp.route('/reservations', methods=['GET'])
@jwt_required()
@admin_required
def list_all_reservations():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=int)
    classroom_id = request.args.get('classroom_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    username = request.args.get('username')
    room_no = request.args.get('room_no')

    pagination = reservation_service.list_all_reservations(
        page, per_page, status, classroom_id, start_date, end_date, username, room_no
    )
    return success(data={
        'items': [r.to_dict(include_user=True, include_classroom=True) for r in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': pagination.page
    })


@admin_bp.route('/reservations/<int:reservation_id>/cancel', methods=['POST'])
@jwt_required()
@admin_required
def admin_cancel_reservation(reservation_id):
    ok, err_msg = reservation_service.admin_cancel_reservation(reservation_id)
    if not ok:
        return error(message=err_msg)
    return success(message='预订已强制取消')


@admin_bp.route('/reservations/<int:reservation_id>/restore', methods=['POST'])
@jwt_required()
@admin_required
def restore_reservation(reservation_id):
    ok, err_msg = reservation_service.restore_reservation(reservation_id)
    if not ok:
        return error(message=err_msg)
    return success(message='预订已恢复')


# Approvals
@admin_bp.route('/approvals/pending', methods=['GET'])
@jwt_required()
@admin_required
def list_pending_approvals():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = approval_service.list_pending_approvals(page, per_page)
    return success(data={
        'items': [r.to_dict(include_user=True, include_classroom=True) for r in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': pagination.page
    })


@admin_bp.route('/approvals/<int:reservation_id>', methods=['POST'])
@jwt_required()
@admin_required
def approve_reservation(reservation_id):
    try:
        data = approval_schema.load(request.get_json())
    except ValidationError as err:
        return error(message='参数错误: ' + str(err.messages))

    admin_id = get_jwt_identity()
    approval, err_msg = approval_service.approve_reservation(
        reservation_id, admin_id, data['result'], data.get('opinion')
    )
    if err_msg:
        return error(message=err_msg)
    return success(data=approval.to_dict(), message='审批完成')


# Statistics
@admin_bp.route('/statistics/usage', methods=['GET'])
@jwt_required()
@admin_required
def usage_statistics():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if not start_date or not end_date:
        return error(message='请提供统计起止日期')

    results = statistics_service.get_usage_statistics(start_date, end_date)
    hot_hours = statistics_service.get_hot_hours(start_date, end_date)
    return success(data={
        'usage': results,
        'hot_hours': hot_hours
    })
