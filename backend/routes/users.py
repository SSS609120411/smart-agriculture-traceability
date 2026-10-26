# -*- coding: utf-8 -*-
"""用户管理（仅管理员）。"""
from flask import Blueprint, request

from extensions import db
from models import User
from utils.auth import role_required
from utils.response import err, ok

users_bp = Blueprint("users", __name__)

VALID_ROLES = ("admin", "producer", "consumer")


@users_bp.route("", methods=["GET"])
@role_required("admin")
def list_users():
    items = User.query.order_by(User.id.asc()).all()
    return ok([u.to_dict() for u in items])


@users_bp.route("", methods=["POST"])
@role_required("admin")
def create_user():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return err("用户名和密码不能为空")
    if User.query.filter_by(username=username).first():
        return err("用户名已存在")
    role = data.get("role", "consumer")
    if role not in VALID_ROLES:
        return err("无效角色")

    user = User(username=username, role=role, name=data.get("name"), phone=data.get("phone"))
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return ok(user.to_dict(), "创建成功")


@users_bp.route("/<int:uid>", methods=["PUT"])
@role_required("admin")
def update_user(uid):
    user = User.query.get(uid)
    if not user:
        return err("用户不存在")
    data = request.get_json(silent=True) or {}
    if data.get("name") is not None:
        user.name = data["name"]
    if data.get("phone") is not None:
        user.phone = data["phone"]
    if data.get("role") in VALID_ROLES:
        user.role = data["role"]
    if data.get("password"):
        user.set_password(data["password"])
    db.session.commit()
    return ok(user.to_dict(), "更新成功")


@users_bp.route("/<int:uid>", methods=["DELETE"])
@role_required("admin")
def delete_user(uid):
    user = User.query.get(uid)
    if not user:
        return err("用户不存在")
    if user.role == "admin":
        return err("不能删除管理员账号")
    db.session.delete(user)
    db.session.commit()
    return ok(message="删除成功")
