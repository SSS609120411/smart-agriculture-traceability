# -*- coding: utf-8 -*-
"""产品管理：查询（登录）、增删改（管理员/生产者）。"""
from flask import Blueprint, request

from extensions import db
from models import Category, Product
from utils.auth import login_required, role_required
from utils.response import err, ok

products_bp = Blueprint("products", __name__)


@products_bp.route("", methods=["GET"])
@login_required
def list_products():
    category_id = request.args.get("category_id", type=int)
    q = Product.query
    if category_id:
        q = q.filter_by(category_id=category_id)
    items = q.order_by(Product.id.desc()).all()

    data = []
    for p in items:
        d = p.to_dict()
        c = Category.query.get(p.category_id)
        d["category_name"] = c.name if c else ""
        data.append(d)
    return ok(data)


@products_bp.route("", methods=["POST"])
@role_required("admin", "producer")
def create_product():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return err("产品名称不能为空")
    if not data.get("category_id") or not Category.query.get(data["category_id"]):
        return err("请选择有效分类")
    p = Product(
        category_id=data["category_id"],
        name=name,
        origin=data.get("origin"),
        variety=data.get("variety"),
        description=data.get("description"),
        image_url=data.get("image_url"),
    )
    db.session.add(p)
    db.session.commit()
    return ok(p.to_dict(), "创建成功")


@products_bp.route("/<int:pid>", methods=["PUT"])
@role_required("admin", "producer")
def update_product(pid):
    p = Product.query.get(pid)
    if not p:
        return err("产品不存在")
    data = request.get_json(silent=True) or {}
    if data.get("category_id") and Category.query.get(data["category_id"]):
        p.category_id = data["category_id"]
    for field in ("name", "origin", "variety", "description", "image_url"):
        if data.get(field) is not None:
            setattr(p, field, data[field])
    db.session.commit()
    return ok(p.to_dict(), "更新成功")


@products_bp.route("/<int:pid>", methods=["DELETE"])
@role_required("admin", "producer")
def delete_product(pid):
    p = Product.query.get(pid)
    if not p:
        return err("产品不存在")
    db.session.delete(p)
    db.session.commit()
    return ok(message="删除成功")
