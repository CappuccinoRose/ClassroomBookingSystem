from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services import reservation_service, periodic_service
from app.schemas.reservation_schema import ReservationCreateSchema, ReservationUpdateSchema, PeriodicRuleSchema
from app.utils.response import success, error, not_found, forbidden

reservation_bp = Blueprint('reservation', __name__, url_prefix='/api/reservations')

create_schema = ReservationCreateSchema()
update_schema = ReservationUpdateSchema()
rule_schema = PeriodicRuleSchema()


@reservation_bp.route('/my', methods=['GET'])
@jwt_required()
def my_reservations():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=int)

    pagination = reservation_service.list_my_reservations(user_id, page, per_page, status)
    return success(data={
        'items': [r.to_dict(include_classroom=True) for r in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': pagination.page
    })


@reservation_bp.route('/<int:reservation_id>', methods=['GET'])
@jwt_required()
def get_reservation(reservation_id):
    user_id = get_jwt_identity()
    reservation = reservation_service.get_reservation(reservation_id, user_id)
    if not reservation:
        return not_found('预订不存在')
    return success(data=reservation.to_dict(include_classroom=True))


@reservation_bp.route('', methods=['POST'])
@jwt_required()
def create_reservation():
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as err:
        return error(message='参数错误: ' + str(err.messages))

    user_id = get_jwt_identity()
    reservation, err_msg = reservation_service.create_reservation(user_id=user_id, **data)
    if err_msg:
        return error(message=err_msg, code=409, status_code=409)
    return success(data=reservation.to_dict(), message='预订成功')


@reservation_bp.route('/<int:reservation_id>', methods=['PUT'])
@jwt_required()
def update_reservation(reservation_id):
    try:
        data = update_schema.load(request.get_json())
    except ValidationError as err:
        return error(message='参数错误: ' + str(err.messages))

    if not data:
        return error(message='无有效更新字段')

    user_id = get_jwt_identity()
    reservation, err_msg = reservation_service.update_reservation(reservation_id, user_id, **data)
    if err_msg:
        return error(message=err_msg, code=409, status_code=409)
    return success(data=reservation.to_dict(), message='预订修改成功')


@reservation_bp.route('/<int:reservation_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_reservation(reservation_id):
    user_id = get_jwt_identity()
    ok, err_msg = reservation_service.cancel_reservation(reservation_id, user_id)
    if not ok:
        return error(message=err_msg)
    return success(message='预订取消成功')


# Periodic rules
@reservation_bp.route('/periodic-rules', methods=['GET'])
@jwt_required()
def list_periodic_rules():
    user_id = get_jwt_identity()
    rules = periodic_service.list_my_rules(user_id)
    return success(data=[r.to_dict(include_classroom=True) for r in rules])


@reservation_bp.route('/periodic-rules', methods=['POST'])
@jwt_required()
def create_periodic_rule():
    try:
        data = rule_schema.load(request.get_json())
    except ValidationError as err:
        return error(message='参数错误: ' + str(err.messages))

    user_id = get_jwt_identity()
    rule, err_msg = periodic_service.create_rule(user_id=user_id, **data)
    if err_msg:
        return error(message=err_msg)
    return success(data=rule.to_dict(), message='周期规则创建成功')


@reservation_bp.route('/periodic-rules/<int:rule_id>/status', methods=['PUT'])
@jwt_required()
def update_rule_status(rule_id):
    data = request.get_json()
    status = data.get('status')
    if status not in [0, 1]:
        return error(message='状态参数错误')

    user_id = get_jwt_identity()
    ok, err_msg = periodic_service.update_rule_status(rule_id, user_id, status)
    if not ok:
        return error(message=err_msg)
    return success(message='规则状态更新成功')


@reservation_bp.route('/periodic-rules/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_rule(rule_id):
    user_id = get_jwt_identity()
    ok, err_msg = periodic_service.delete_rule(rule_id, user_id)
    if not ok:
        return error(message=err_msg)
    return success(message='规则删除成功')
