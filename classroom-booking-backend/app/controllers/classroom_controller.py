from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.services import classroom_service
from app.schemas.classroom_schema import ClassroomCreateSchema, ClassroomUpdateSchema, FreeClassroomQuerySchema
from app.utils.response import success, error, not_found
from app.utils.decorators import admin_required

classroom_bp = Blueprint('classroom', __name__, url_prefix='/api/classrooms')

create_schema = ClassroomCreateSchema()
update_schema = ClassroomUpdateSchema()
free_query_schema = FreeClassroomQuerySchema()


@classroom_bp.route('', methods=['GET'])
@jwt_required()
def list_classrooms():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    floor = request.args.get('floor', type=int)
    min_capacity = request.args.get('min_capacity', type=int)
    status = request.args.get('status', type=int)

    pagination = classroom_service.list_classrooms(page, per_page, floor, min_capacity, status)
    return success(data={
        'items': [c.to_dict() for c in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': pagination.page
    })


@classroom_bp.route('/<int:classroom_id>', methods=['GET'])
@jwt_required()
def get_classroom(classroom_id):
    classroom = classroom_service.get_classroom(classroom_id)
    if not classroom:
        return not_found('教室不存在')
    return success(data=classroom.to_dict())


@classroom_bp.route('/free', methods=['GET'])
@jwt_required()
def find_free():
    try:
        data = free_query_schema.load(request.args.to_dict())
    except ValidationError as err:
        return error(message='参数错误: ' + str(err.messages))

    classrooms = classroom_service.find_free_classrooms(**data)
    return success(data=[c.to_dict() for c in classrooms])


@classroom_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_classroom():
    try:
        data = create_schema.load(request.get_json())
    except ValidationError as err:
        return error(message='参数错误: ' + str(err.messages))

    classroom, err_msg = classroom_service.create_classroom(**data)
    if err_msg:
        return error(message=err_msg)
    return success(data=classroom.to_dict(), message='教室创建成功')


@classroom_bp.route('/<int:classroom_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_classroom(classroom_id):
    try:
        data = update_schema.load(request.get_json())
    except ValidationError as err:
        return error(message='参数错误: ' + str(err.messages))

    if not data:
        return error(message='无有效更新字段')

    classroom, err_msg = classroom_service.update_classroom(classroom_id, **data)
    if err_msg:
        return error(message=err_msg)
    return success(data=classroom.to_dict(), message='教室更新成功')


@classroom_bp.route('/<int:classroom_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_classroom(classroom_id):
    ok, err_msg = classroom_service.delete_classroom(classroom_id)
    if not ok:
        return error(message=err_msg)
    return success(message='教室删除成功')
