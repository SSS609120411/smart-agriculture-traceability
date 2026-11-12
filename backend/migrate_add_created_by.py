# -*- coding: utf-8 -*-
"""数据库迁移：为 products 表补 created_by 字段（幂等，可重复执行）。

背景：权限模型从"角色级"升级为"角色+归属"双校验，产品需要记录创建人。
db.create_all() 不会给已存在的表加列，所以需要本脚本。

用法（在 backend 目录下，先激活虚拟环境）：
    python migrate_add_created_by.py

行为：
    1. 若 products 表已无 created_by 列 -> ALTER TABLE 添加
    2. 把 created_by 为空、且已有批次的产品，按批次的 producer_id 回填归属
    3. 仍为空的产品视为平台数据，仅管理员可改删
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import inspect, text

from app import app
from extensions import db


def migrate():
    with app.app_context():
        inspector = inspect(db.engine)
        if "products" not in inspector.get_table_names():
            print("products 表不存在，请先执行 python seed.py 初始化。")
            return 1

        cols = [c["name"] for c in inspector.get_columns("products")]
        if "created_by" in cols:
            print("products.created_by 已存在，跳过加列。")
        else:
            db.session.execute(text("ALTER TABLE products ADD COLUMN created_by INTEGER"))
            db.session.commit()
            print("已为 products 表添加 created_by 列。")

        # 回填：有批次的产品，取该批次的生产者作为创建人
        updated = db.session.execute(text("""
            UPDATE products
               SET created_by = (
                   SELECT b.producer_id FROM batches b
                    WHERE b.product_id = products.id
                    ORDER BY b.id ASC
                    LIMIT 1
               )
             WHERE created_by IS NULL
               AND EXISTS (SELECT 1 FROM batches b WHERE b.product_id = products.id)
        """)).rowcount
        db.session.commit()
        print(f"已按批次归属回填 {updated} 个产品的创建人。")

        left = db.session.execute(text(
            "SELECT COUNT(*) FROM products WHERE created_by IS NULL"
        )).scalar()
        print(f"仍无归属的产品 {left} 个（视为平台数据，仅管理员可改删）。")
        return 0


if __name__ == "__main__":
    sys.exit(migrate())
