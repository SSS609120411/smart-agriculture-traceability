# -*- coding: utf-8 -*-
"""冒烟测试：使用 SQLite + Flask 测试客户端跑通核心流程。

用法（在 backend 目录下）：
    $env:DATABASE_URL = "sqlite:///test.db"   # PowerShell
    python smoke_test.py
"""
import os
import sys

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db

app = create_app()
app.config["TESTING"] = True

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


def run():
    with app.app_context():
        db.create_all()
    c = app.test_client()

    print("== 登录 ==")
    r = c.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    check("管理员登录", r.status_code == 200 and r.get_json()["code"] == 0, r.get_json())
    admin_token = r.get_json()["data"]["token"]

    r = c.post("/api/auth/login", json={"username": "producer", "password": "producer123"})
    check("生产者登录", r.status_code == 200 and r.get_json()["code"] == 0, r.get_json())
    producer_token = r.get_json()["data"]["token"]

    r = c.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    check("错误密码被拒绝", r.status_code == 401, r.status_code)

    ah = {"Authorization": f"Bearer {admin_token}"}
    ph = {"Authorization": f"Bearer {producer_token}"}

    print("== 分类 ==")
    r = c.get("/api/categories", headers=ah)
    check("分类列表", r.status_code == 200 and len(r.get_json()["data"]) >= 6, r.get_json())
    r = c.post("/api/categories", headers=ah, json={"name": "花卉", "description": "花卉类"})
    check("新增分类", r.status_code == 200, r.get_json())
    cat_id = r.get_json()["data"]["id"]

    print("== 产品 ==")
    r = c.post("/api/products", headers=ph, json={"category_id": cat_id, "name": "有机番茄", "origin": "南京", "variety": "粉果"})
    check("生产者新增产品", r.status_code == 200, r.get_json())
    pid = r.get_json()["data"]["id"]

    print("== 批次 ==")
    r = c.post("/api/batches", headers=ph, json={"product_id": pid, "production_date": "2026-09-25", "quantity": "100", "unit": "kg", "status": "生产中"})
    check("创建批次", r.status_code == 200 and r.get_json()["data"].get("trace_code"), r.get_json())
    bid = r.get_json()["data"]["id"]
    trace_code = r.get_json()["data"]["trace_code"]
    check("生成二维码", bool(r.get_json()["data"].get("qr_code")), r.get_json()["data"].get("qr_code"))

    print("== 环节记录 ==")
    r = c.post(f"/api/batches/{bid}/records/planting", headers=ph, json={"record_type": "播种", "detail": "定植", "record_date": "2026-09-26", "location": "2号棚"})
    check("新增种植记录", r.status_code == 200, r.get_json())
    r = c.post(f"/api/batches/{bid}/records/quality", headers=ph, json={"inspect_date": "2026-09-27", "inspector": "王质检", "items": "农残", "result": "合格"})
    check("新增质检记录", r.status_code == 200, r.get_json())

    print("== 溯源查询（公开） ==")
    r = c.get(f"/api/trace/{trace_code}")
    j = r.get_json()
    check("公开溯源查询", r.status_code == 200 and len(j["data"]["timeline"]) == 2, j)
    check("溯源含产品信息", j["data"]["product"] is not None)
    r = c.get("/api/trace/TR_NOT_EXIST")
    check("无效溯源码返回404", r.status_code == 404, r.status_code)

    print("== 看板统计 ==")
    r = c.get("/api/dashboard/stats", headers=ah)
    check("看板统计", r.status_code == 200 and r.get_json()["data"]["batch_count"] >= 2, r.get_json())

    print("== 权限 ==")
    r = c.get("/api/users", headers=ph)
    check("生产者访问用户管理被拒(403)", r.status_code == 403, r.status_code)

    print(f"\n结果：通过 {PASS}，失败 {FAIL}")
    return FAIL == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
