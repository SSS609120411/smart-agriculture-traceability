# -*- coding: utf-8 -*-
"""批次管理：核心溯源单元，创建时自动生成溯源码 + 二维码。"""
from flask import Blueprint, g, request

from extensions import db
from models import Batch, Product
from utils.auth import login_required, role_required
from utils.qrcode import generate_qrcode, generate_trace_code
from utils.response import err, ok

batches_bp = Blueprint("batches", __name__)


def _with_product_name(b):
    d = b.to_dict()
    p = Product.query.get(b.product_id)
    d["product_name"] = p.name if p else ""
    return d


@batches_bp.route("", methods=["GET"])
@login_required
def list_batches():
    q = Batch.query
    if g.user.role == "producer":
        q = q.filter(Batch.producer_id == g.user.id)
    items = q.order_by(Batch.id.desc()).all()
    return ok([_with_product_name(b) for b in items])


@batches_bp.route("", methods=["POST"])
@role_required("admin", "producer")
def create_batch():
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    if not product_id or not Product.query.get(product_id):
        return err("请选择有效产品")

    batch = Batch(
        product_id=product_id,
        producer_id=g.user.id,
        trace_code=generate_trace_code(),
        production_date=data.get("production_date"),
        quantity=data.get("quantity"),
        unit=data.get("unit"),
        status=data.get("status") or "生产中",
    )
    db.session.add(batch)
    db.session.flush()
    batch.qr_code = generate_qrcode(batch.trace_code)
    db.session.commit()
    return ok(_with_product_name(batch), "批次创建成功")


@batches_bp.route("/<int:bid>", methods=["GET"])
@login_required
def get_batch(bid):
    b = Batch.query.get(bid)
    if not b:
        return err("批次不存在", 404)
    return ok(_with_product_name(b))


@batches_bp.route("/<int:bid>/qrcode", methods=["GET"])
@login_required
def get_qrcode(bid):
    b = Batch.query.get(bid)
    if not b:
        return err("批次不存在", 404)
    return ok({"trace_code": b.trace_code, "qr_code": b.qr_code})


@batches_bp.route("/<int:bid>", methods=["PUT"])
@role_required("admin", "producer")
def update_batch(bid):
    b = Batch.query.get(bid)
    if not b:
        return err("批次不存在", 404)
    data = request.get_json(silent=True) or {}
    for field in ("production_date", "quantity", "unit", "status"):
        if data.get(field) is not None:
            setattr(b, field, data[field])
    if data.get("product_id") and Product.query.get(data["product_id"]):
        b.product_id = data["product_id"]
    db.session.commit()
    return ok(_with_product_name(b), "更新成功")


@batches_bp.route("/<int:bid>", methods=["DELETE"])
@role_required("admin", "producer")
def delete_batch(bid):
    b = Batch.query.get(bid)
    if not b:
        return err("批次不存在", 404)
    db.session.delete(b)
    db.session.commit()
    return ok(message="删除成功")
