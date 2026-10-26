# -*- coding: utf-8 -*-
"""初始化数据库：建表 + 种子数据（管理员、示例产品、示例批次及全链路记录）。

用法（在 backend 目录下）：
    python seed.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models import (Batch, Category, LogisticsRecord, PlantingRecord, ProcessingRecord,
                    Product, QualityInspection, SalesRecord, User)
from utils.qrcode import generate_qrcode, generate_trace_code

app = create_app()


def seed():
    with app.app_context():
        db.create_all()

        # 用户
        if not User.query.filter_by(username="admin").first():
            u = User(username="admin", role="admin", name="系统管理员", phone="13800000000")
            u.set_password("admin123")
            db.session.add(u)
        if not User.query.filter_by(username="producer").first():
            u = User(username="producer", role="producer", name="张农户", phone="13900000001")
            u.set_password("producer123")
            db.session.add(u)
        if not User.query.filter_by(username="consumer").first():
            u = User(username="consumer", role="consumer", name="李消费者", phone="13700000002")
            u.set_password("consumer123")
            db.session.add(u)
        db.session.commit()

        # 分类
        cats = {}
        for name in ("蔬菜", "水果", "粮食", "畜禽", "水产", "茶叶"):
            c = Category.query.filter_by(name=name).first()
            if not c:
                c = Category(name=name, description=f"{name}类农产品")
                db.session.add(c)
                db.session.flush()
            cats[name] = c
        db.session.commit()

        # 示例产品 + 示例批次（含全链路记录，便于演示溯源）
        if not Product.query.filter_by(name="有机草莓").first():
            producer = User.query.filter_by(username="producer").first()
            p = Product(
                category_id=cats["水果"].id, name="有机草莓", origin="江苏省南京市溧水区",
                variety="红颜", description="绿色有机种植，无公害，全程可溯源",
            )
            db.session.add(p)
            db.session.flush()

            code = generate_trace_code()
            b = Batch(
                product_id=p.id, producer_id=producer.id, trace_code=code,
                production_date="2026-09-20", quantity="500", unit="kg", status="已上市",
            )
            db.session.add(b)
            db.session.flush()
            b.qr_code = generate_qrcode(code)

            db.session.add_all([
                PlantingRecord(batch_id=b.id, record_type="播种", detail="有机草莓苗定植", record_date="2026-03-15", location="1号大棚"),
                PlantingRecord(batch_id=b.id, record_type="施肥", detail="施用有机肥 20kg/亩", record_date="2026-04-10", location="1号大棚"),
                PlantingRecord(batch_id=b.id, record_type="灌溉", detail="滴灌，保持土壤湿润", record_date="2026-04-12", location="1号大棚"),
                QualityInspection(batch_id=b.id, inspect_date="2026-09-18", inspector="王质检",
                                  items="农药残留、重金属", result="合格", report_url="QA-2026-0918"),
                ProcessingRecord(batch_id=b.id, process_date="2026-09-19", process_type="分拣包装",
                                 detail="按 500g/盒 分级包装", operator="张农户"),
                LogisticsRecord(batch_id=b.id, transport_date="2026-09-20", from_place="南京溧水基地",
                                to_place="南京市区配送中心", carrier="冷链物流", temperature="4℃"),
                SalesRecord(batch_id=b.id, sale_date="2026-09-21", channel="电商平台",
                            quantity="200", price="39.9", buyer="南京生鲜超市"),
            ])
            db.session.commit()
            print(f"示例批次溯源码：{code}")

    print("初始化完成！")
    print("  管理员：admin / admin123")
    print("  生产者：producer / producer123")
    print("  消费者：consumer / consumer123")


if __name__ == "__main__":
    seed()
