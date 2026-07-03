from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services import auth_service
from app.schemas.auth_schema import RegisterSchema, LoginSchema, ChangePasswordSchema
from app.utils.response import success, error, unauthorized

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

register_schema = RegisterSchema()
login_schema = LoginSchema()
change_password_schema = ChangePasswordSchema()


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = register_schema.load(request.get_json())
    except ValidationError as err:
        return error(message='参数错误: ' + str(err.messages))

    user, err_msg = auth_service.register_user(**data)
    if err_msg:
        return error(message=err_msg)
    return success(data=user.to_dict(), message='注册成功')


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return error(message='参数错误: ' + str(err.messages))

    result, err_msg = auth_service.login_user(**data)
    if err_msg:
        return error(message=err_msg)
    return success(data=result, message='登录成功')


@auth_bp.route('/userinfo', methods=['GET'])
@jwt_required()
def userinfo():
    user_id = get_jwt_identity()
    user = auth_service.get_user_by_id(user_id)
    if not user:
        return unauthorized()
    return success(data=user.to_dict())


@auth_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        data = change_password_schema.load(request.get_json())
    except ValidationError as err:
        return error(message='参数错误: ' + str(err.messages))

    user_id = get_jwt_identity()
    ok, err_msg = auth_service.change_password(user_id, data['old_password'], data['new_password'])
    if not ok:
        return error(message=err_msg)
    return success(message='密码修改成功')
