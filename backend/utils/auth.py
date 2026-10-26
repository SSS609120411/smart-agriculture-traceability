# -*- coding: utf-8 -*-
"""JWT 签发、校验与鉴权装饰器。"""
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from utils.response import err


def generate_token(user):
    payload = {
        "sub": user.id,
        "role": user.role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=current_app.config["JWT_EXPIRES_HOURS"]),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def _decode(token):
    try:
        return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_current_user():
    from models import User

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    payload = _decode(auth[7:])
    if not payload:
        return None
    return User.query.get(payload["sub"])


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return err("请先登录", 401)
        g.user = user
        return f(*args, **kwargs)

    return wrapper


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                return err("请先登录", 401)
            if user.role not in roles:
                return err("无操作权限", 403)
            g.user = user
            return f(*args, **kwargs)

        return wrapper

    return decorator
