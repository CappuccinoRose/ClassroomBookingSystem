from flask import jsonify


def success(data=None, message='操作成功', code=200):
    return jsonify({'code': code, 'message': message, 'data': data}), 200


def error(message='操作失败', code=400, status_code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), status_code


def unauthorized(message='未登录或Token无效'):
    return error(message, code=401, status_code=401)


def forbidden(message='无权限访问'):
    return error(message, code=403, status_code=403)


def not_found(message='资源不存在'):
    return error(message, code=404, status_code=404)


def conflict(message='业务冲突'):
    return error(message, code=409, status_code=409)
