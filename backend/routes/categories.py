# -*- coding: utf-8 -*-
"""产品分类：查询（登录）、增删改（仅管理员）。"""
from flask import Blueprint, request

from extensions import db
from models import Category, Product
from utils.auth import login_required, role_required
from utils.response import err, ok

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("", methods=["GET"])
@login_required
def list_categories():
    items = Category.query.order_by(Category.id.asc()).all()
    return ok([c.to_dict() for c in items])


@categories_bp.route("", methods=["POST"])
@role_required("admin")
def create_category():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return err("分类名称不能为空")
    if Category.query.filter_by(name=name).first():
        return err("分类已存在")
    c = Category(name=name, description=data.get("description"))
    db.session.add(c)
    db.session.commit()
    return ok(c.to_dict(), "创建成功")


@categories_bp.route("/<int:cid>", methods=["PUT"])
@role_required("admin")
def update_category(cid):
    c = Category.query.get(cid)
    if not c:
        return err("分类不存在")
    data = request.get_json(silent=True) or {}
    if data.get("name") is not None:
        c.name = data["name"]
    if data.get("description") is not None:
        c.description = data["description"]
    db.session.commit()
    return ok(c.to_dict(), "更新成功")


@categories_bp.route("/<int:cid>", methods=["DELETE"])
@role_required("admin")
def delete_category(cid):
    c = Category.query.get(cid)
    if not c:
        return err("分类不存在")
    if Product.query.filter_by(category_id=cid).first():
        return err("该分类下存在产品，无法删除")
    db.session.delete(c)
    db.session.commit()
    return ok(message="删除成功")
