import bcrypt
from app.models.user import User
from app.extensions import db
from flask_jwt_extended import create_access_token


def register_user(username, password, email):
    if User.query.filter_by(username=username).first():
        return None, '账号已存在'
    if User.query.filter_by(email=email).first():
        return None, '邮箱已被注册'

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(username=username, password_hash=password_hash, email=email, role=0, status=1)
    db.session.add(user)
    db.session.commit()
    return user, None


def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        return None, '账号或密码错误'
    if user.status == 0:
        return None, '账号已被禁用'
    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return None, '账号或密码错误'

    token = create_access_token(identity=str(user.user_id))
    return {'token': token, 'user': user.to_dict()}, None


def get_user_by_id(user_id):
    return User.query.get(user_id)


def change_password(user_id, old_password, new_password):
    user = User.query.get(user_id)
    if not user:
        return False, '用户不存在'
    if not bcrypt.checkpw(old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return False, '原密码错误'

    user.password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.session.commit()
    return True, None
