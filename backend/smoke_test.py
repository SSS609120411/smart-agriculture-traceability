# -*- coding: utf-8 -*-
"""冒烟测试：使用 SQLite + Flask 测试客户端跑通核心流程。

用法（在 backend 目录下）：
    $env:DATABASE_URL = "sqlite:///test.db"   # PowerShell
    python smoke_test.py
"""
import os
import sys
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 每次使用全新的临时库，避免旧表结构(缺少 created_by)造成误判
TEST_DB = os.path.join(tempfile.gettempdir(), "trace_smoke_test.db")
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
os.environ["DATABASE_URL"] = "sqlite:///" + TEST_DB.replace("\\", "/")
sys.path.insert(0, BASE_DIR)

from app import create_app
from extensions import db

app = create_app()
app.config["TESTING"] = True
app.config["QR_DIR"] = os.path.join(tempfile.gettempdir(), "trace_qr_test")

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


def seed_minimal():
    """最小种子：3 个账号 + 6 个分类（测试库独立，不依赖 seed.py 的既有数据）。"""
    from models import Category, User

    for username, role, name, pwd in (
        ("admin", "admin", "系统管理员", "admin123"),
        ("producer", "producer", "张农户", "producer123"),
        ("consumer", "consumer", "李消费者", "consumer123"),
    ):
        if not User.query.filter_by(username=username).first():
            u = User(username=username, role=role, name=name)
            u.set_password(pwd)
            db.session.add(u)

    for name in ("蔬菜", "水果", "粮食", "畜禽", "水产", "茶叶"):
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name, description=f"{name}类农产品"))

    db.session.commit()


def run():
    with app.app_context():
        db.create_all()
        seed_minimal()
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
    check("看板统计", r.status_code == 200 and r.get_json()["data"]["batch_count"] >= 1, r.get_json())

    print("== 权限：角色 ==")
    r = c.get("/api/users", headers=ph)
    check("生产者访问用户管理被拒(403)", r.status_code == 403, r.status_code)
    r = c.get("/api/categories", headers=ph)
    check("生产者可读分类(200)", r.status_code == 200)
    r = c.post("/api/categories", headers=ph, json={"name": "生产者越权分类"})
    check("生产者新增分类被拒(403)", r.status_code == 403, r.status_code)

    print("== 权限：数据归属 ==")
    r = c.post("/api/users", headers=ah, json={
        "username": "producer2", "password": "producer123", "role": "producer", "name": "李农户"})
    check("管理员创建第二个生产者", r.status_code == 200, r.get_json())
    r = c.post("/api/auth/login", json={"username": "producer2", "password": "producer123"})
    check("第二个生产者登录", r.status_code == 200, r.get_json())
    p2h = {"Authorization": f"Bearer {r.get_json()['data']['token']}"}

    # 产品归属：pid 由 producer 创建
    r = c.delete(f"/api/products/{pid}", headers=p2h)
    check("生产者2删除他人产品被拒(403)", r.status_code == 403, r.get_json())
    r = c.put(f"/api/products/{pid}", headers=p2h, json={"name": "改别人的"})
    check("生产者2修改他人产品被拒(403)", r.status_code == 403, r.get_json())
    r = c.delete(f"/api/products/{pid}", headers=ph)
    check("生产者删除自己的产品(200)", r.status_code == 200, r.get_json())

    # 无归属的历史产品：仅管理员可删
    with app.app_context():
        from models import Product as _P
        legacy = _P(category_id=cat_id, name="历史遗留产品")
        db.session.add(legacy)
        db.session.commit()
        legacy_id = legacy.id
    r = c.delete(f"/api/products/{legacy_id}", headers=ph)
    check("生产者删除无归属产品被拒(403)", r.status_code == 403, r.get_json())
    r = c.delete(f"/api/products/{legacy_id}", headers=ah)
    check("管理员删除无归属产品(200)", r.status_code == 200, r.get_json())

    # 批次归属：bid 属于 producer
    r = c.delete(f"/api/batches/{bid}", headers=p2h)
    check("生产者2删除他人批次被拒(403)", r.status_code == 403, r.get_json())
    r = c.put(f"/api/batches/{bid}", headers=p2h, json={"status": "已上市"})
    check("生产者2修改他人批次被拒(403)", r.status_code == 403, r.get_json())
    r = c.put(f"/api/batches/{bid}", headers=ph, json={"status": "已上市"})
    check("生产者修改自己的批次(200)", r.status_code == 200, r.get_json())

    # 记录归属：只能操作自己批次的记录
    r = c.post(f"/api/batches/{bid}/records/planting", headers=p2h, json={"record_type": "施肥", "detail": "越权写入"})
    check("生产者2向他人批次加记录被拒(403)", r.status_code == 403, r.get_json())
    r = c.get(f"/api/batches/{bid}/records/planting", headers=ph)
    rid = r.get_json()["data"][0]["id"]
    r = c.delete(f"/api/batches/records/planting/{rid}", headers=p2h)
    check("生产者2删除他人批次记录被拒(403)", r.status_code == 403, r.get_json())
    r = c.delete(f"/api/batches/records/planting/{rid}", headers=ph)
    check("生产者删除自己的批次记录(200)", r.status_code == 200, r.get_json())

    # 管理员不受归属限制
    r = c.delete(f"/api/batches/{bid}", headers=ah)
    check("管理员删除他人批次(200)", r.status_code == 200, r.get_json())

    print(f"\n结果：通过 {PASS}，失败 {FAIL}")
    return FAIL == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
