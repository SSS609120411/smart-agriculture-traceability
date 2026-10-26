# -*- coding: utf-8 -*-
"""数据库模型：10 张表。"""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="consumer")  # admin / producer / consumer
    name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "name": self.name,
            "phone": self.phone,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    origin = db.Column(db.String(128))   # 产地
    variety = db.Column(db.String(128))  # 品种
    description = db.Column(db.String(512))
    image_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "name": self.name,
            "origin": self.origin,
            "variety": self.variety,
            "description": self.description,
            "image_url": self.image_url,
        }


class Batch(db.Model):
    __tablename__ = "batches"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    producer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trace_code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    qr_code = db.Column(db.String(256))
    production_date = db.Column(db.String(20))
    quantity = db.Column(db.String(64))
    unit = db.Column(db.String(20))
    status = db.Column(db.String(20), default="生产中")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "producer_id": self.producer_id,
            "trace_code": self.trace_code,
            "qr_code": self.qr_code,
            "production_date": self.production_date,
            "quantity": self.quantity,
            "unit": self.unit,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
        }


class PlantingRecord(db.Model):
    __tablename__ = "planting_records"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    record_type = db.Column(db.String(32))  # 播种/施肥/用药/灌溉/采摘
    detail = db.Column(db.String(512))
    record_date = db.Column(db.String(20))
    location = db.Column(db.String(128))

    def to_dict(self):
        return {
            "id": self.id, "batch_id": self.batch_id, "stage": "planting",
            "record_type": self.record_type, "detail": self.detail,
            "record_date": self.record_date, "location": self.location,
        }


class QualityInspection(db.Model):
    __tablename__ = "quality_inspections"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    inspect_date = db.Column(db.String(20))
    inspector = db.Column(db.String(64))
    items = db.Column(db.String(256))
    result = db.Column(db.String(20))
    report_url = db.Column(db.String(256))

    def to_dict(self):
        return {
            "id": self.id, "batch_id": self.batch_id, "stage": "quality",
            "inspect_date": self.inspect_date, "inspector": self.inspector,
            "items": self.items, "result": self.result, "report_url": self.report_url,
        }


class ProcessingRecord(db.Model):
    __tablename__ = "processing_records"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    process_date = db.Column(db.String(20))
    process_type = db.Column(db.String(64))
    detail = db.Column(db.String(512))
    operator = db.Column(db.String(64))

    def to_dict(self):
        return {
            "id": self.id, "batch_id": self.batch_id, "stage": "processing",
            "process_date": self.process_date, "process_type": self.process_type,
            "detail": self.detail, "operator": self.operator,
        }


class LogisticsRecord(db.Model):
    __tablename__ = "logistics_records"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    transport_date = db.Column(db.String(20))
    from_place = db.Column(db.String(128))
    to_place = db.Column(db.String(128))
    carrier = db.Column(db.String(64))
    temperature = db.Column(db.String(32))

    def to_dict(self):
        return {
            "id": self.id, "batch_id": self.batch_id, "stage": "logistics",
            "transport_date": self.transport_date, "from_place": self.from_place,
            "to_place": self.to_place, "carrier": self.carrier, "temperature": self.temperature,
        }


class SalesRecord(db.Model):
    __tablename__ = "sales_records"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    sale_date = db.Column(db.String(20))
    channel = db.Column(db.String(64))
    quantity = db.Column(db.String(64))
    price = db.Column(db.String(32))
    buyer = db.Column(db.String(128))

    def to_dict(self):
        return {
            "id": self.id, "batch_id": self.batch_id, "stage": "sales",
            "sale_date": self.sale_date, "channel": self.channel,
            "quantity": self.quantity, "price": self.price, "buyer": self.buyer,
        }


class TraceLog(db.Model):
    __tablename__ = "trace_logs"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False)
    query_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip = db.Column(db.String(64))

    def to_dict(self):
        return {
            "id": self.id, "batch_id": self.batch_id,
            "query_time": self.query_time.strftime("%Y-%m-%d %H:%M:%S") if self.query_time else None,
            "ip": self.ip,
        }
