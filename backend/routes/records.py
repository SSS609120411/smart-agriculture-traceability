# -*- coding: utf-8 -*-
"""各环节溯源记录：种植 / 质检 / 加工 / 物流 / 销售。"""
from flask import Blueprint, request

from extensions import db
from models import (Batch, LogisticsRecord, PlantingRecord, ProcessingRecord,
                    QualityInspection, SalesRecord)
from utils.auth import login_required, role_required
from utils.response import err, ok

records_bp = Blueprint("records", __name__, url_prefix="/api/batches")

# 环节 -> (模型, 允许写入字段)
STAGES = {
    "planting": (PlantingRecord, ["record_type", "detail", "record_date", "location"]),
    "quality": (QualityInspection, ["inspect_date", "inspector", "items", "result", "report_url"]),
    "processing": (ProcessingRecord, ["process_date", "process_type", "detail", "operator"]),
    "logistics": (LogisticsRecord, ["transport_date", "from_place", "to_place", "carrier", "temperature"]),
    "sales": (SalesRecord, ["sale_date", "channel", "quantity", "price", "buyer"]),
}


@records_bp.route("/<int:batch_id>/records/<stage>", methods=["GET"])
@login_required
def list_records(batch_id, stage):
    if stage not in STAGES:
        return err("未知环节")
    if not Batch.query.get(batch_id):
        return err("批次不存在", 404)
    model, _ = STAGES[stage]
    items = model.query.filter_by(batch_id=batch_id).order_by(model.id.asc()).all()
    return ok([i.to_dict() for i in items])


@records_bp.route("/<int:batch_id>/records/<stage>", methods=["POST"])
@role_required("admin", "producer")
def add_record(batch_id, stage):
    if stage not in STAGES:
        return err("未知环节")
    if not Batch.query.get(batch_id):
        return err("批次不存在", 404)
    model, fields = STAGES[stage]
    data = request.get_json(silent=True) or {}
    kwargs = {k: data.get(k) for k in fields}
    rec = model(batch_id=batch_id, **kwargs)
    db.session.add(rec)
    db.session.commit()
    return ok(rec.to_dict(), "记录已添加")


@records_bp.route("/records/<stage>/<int:record_id>", methods=["DELETE"])
@role_required("admin", "producer")
def delete_record(stage, record_id):
    if stage not in STAGES:
        return err("未知环节")
    model, _ = STAGES[stage]
    rec = model.query.get(record_id)
    if not rec:
        return err("记录不存在", 404)
    db.session.delete(rec)
    db.session.commit()
    return ok(message="删除成功")
