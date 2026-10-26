# -*- coding: utf-8 -*-
"""应用配置：优先从 backend/.env 读取，未提供时使用默认值。"""
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "traceability-secret-key-2026")
    JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", "24"))

    # MySQL 连接（默认值仅供本地示例，实际请在 .env 中修改）
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
    MYSQL_DB = os.getenv("MYSQL_DB", "traceability")

    # 数据库引擎可配置：默认 MySQL；自测时可用 sqlite:///traceability.db
    DATABASE_URL = os.getenv("DATABASE_URL") or (
        f"mysql+pymysql://{quote_plus(MYSQL_USER)}:{quote_plus(MYSQL_PASSWORD)}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}

    # 二维码图片保存目录 & 溯源页前缀（二维码内容 = 前缀 + 溯源码）
    QR_DIR = os.path.join(BASE_DIR, "static", "qrcodes")
    TRACE_PAGE_PREFIX = os.getenv("TRACE_PAGE_PREFIX", "http://127.0.0.1:5173/#/trace/")
