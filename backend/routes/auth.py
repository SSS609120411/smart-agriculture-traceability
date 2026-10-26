# -*- coding: utf-8 -*-
"""认证：登录 / 注册 / 当前用户。"""
from flask import Blueprint, g, request

from extensions import db
from models import User
from utils.auth import generate_token, login_required
from utils.response import err, ok

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return err("用户名或密码错误", 401)

    token = generate_token(user)
    return ok({"token": token, "user": user.to_dict()}, "登录成功")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return err("用户名和密码不能为空")
    if User.query.filter_by(username=username).first():
        return err("用户名已存在")

    user = User(
        username=username,
        role="consumer",  # 自助注册默认消费者，生产者/管理员由管理员创建
        name=data.get("name") or username,
        phone=data.get("phone"),
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return ok(user.to_dict(), "注册成功")


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return ok(g.user.to_dict())
