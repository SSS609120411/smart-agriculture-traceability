# -*- coding: utf-8 -*-
"""公开溯源查询：输入溯源码返回全链路时间轴。"""
from flask import Blueprint, request

from extensions import db
from models import (Batch, Category, LogisticsRecord, PlantingRecord, ProcessingRecord,
                    Product, QualityInspection, SalesRecord, TraceLog, User)
from utils.response import err, ok

trace_bp = Blueprint("trace", __name__)


def _item(stage, time, title, detail, extra=None):
    e = {k: v for k, v in (extra or {}).items() if v not in (None, "")}
    return {"stage": stage, "time": time, "title": title, "detail": detail, "extra": e}


@trace_bp.route("/<trace_code>", methods=["GET"])
def get_trace(trace_code):
    batch = Batch.query.filter_by(trace_code=trace_code.strip()).first()
    if not batch:
        return err("溯源码不存在或无效", 404)

    product = Product.query.get(batch.product_id)
    producer = User.query.get(batch.producer_id)
    category = Category.query.get(product.category_id) if product else None

    timeline = []
    for r in PlantingRecord.query.filter_by(batch_id=batch.id).all():
        timeline.append(_item("种植", r.record_date, r.record_type, r.detail, {"位置": r.location}))
    for r in QualityInspection.query.filter_by(batch_id=batch.id).all():
        timeline.append(_item("质检", r.inspect_date, "质量检测", r.items,
                              {"检测人": r.inspector, "结果": r.result, "报告": r.report_url}))
    for r in ProcessingRecord.query.filter_by(batch_id=batch.id).all():
        timeline.append(_item("加工", r.process_date, r.process_type, r.detail, {"操作人": r.operator}))
    for r in LogisticsRecord.query.filter_by(batch_id=batch.id).all():
        timeline.append(_item("物流", r.transport_date, "运输配送", f"{r.from_place} → {r.to_place}",
                              {"承运方": r.carrier, "温度": r.temperature}))
    for r in SalesRecord.query.filter_by(batch_id=batch.id).all():
        timeline.append(_item("销售", r.sale_date, r.channel, r.buyer,
                              {"数量": r.quantity, "价格": r.price}))

    timeline.sort(key=lambda x: x["time"] or "")

    # 记录查询日志
    db.session.add(TraceLog(batch_id=batch.id, ip=request.remote_addr))
    db.session.commit()

    data = {
        "batch": batch.to_dict(),
        "product": product.to_dict() if product else None,
        "category": category.to_dict() if category else None,
        "producer": {"name": producer.name, "phone": producer.phone} if producer else None,
        "timeline": timeline,
    }
    return ok(data)
