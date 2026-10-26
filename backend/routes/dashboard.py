# -*- coding: utf-8 -*-
"""数据看板统计。"""
from flask import Blueprint

from models import (Batch, Category, LogisticsRecord, PlantingRecord, ProcessingRecord,
                    Product, QualityInspection, SalesRecord, User)
from utils.auth import login_required
from utils.response import ok

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/stats", methods=["GET"])
@login_required
def stats():
    # 分类 -> 产品数
    cat_dist = []
    for c in Category.query.all():
        cnt = Product.query.filter_by(category_id=c.id).count()
        cat_dist.append({"name": c.name, "value": cnt})

    # 批次状态分布
    status_map = {}
    for b in Batch.query.all():
        s = b.status or "未知"
        status_map[s] = status_map.get(s, 0) + 1
    status_dist = [{"name": k, "value": v} for k, v in status_map.items()]

    stage_stats = [
        {"name": "种植", "value": PlantingRecord.query.count()},
        {"name": "质检", "value": QualityInspection.query.count()},
        {"name": "加工", "value": ProcessingRecord.query.count()},
        {"name": "物流", "value": LogisticsRecord.query.count()},
        {"name": "销售", "value": SalesRecord.query.count()},
    ]

    return ok({
        "product_count": Product.query.count(),
        "batch_count": Batch.query.count(),
        "user_count": User.query.count(),
        "category_count": Category.query.count(),
        "category_dist": cat_dist,
        "status_dist": status_dist,
        "stage_stats": stage_stats,
    })
