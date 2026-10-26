# -*- coding: utf-8 -*-
"""
PythonAnywhere WSGI 配置模板。

使用方法：
1. 在 PythonAnywhere 的 Web 页面点击 WSGI configuration file 链接；
2. 用本文件内容整体替换原文件；
3. 把 YOUR_USERNAME 和仓库目录名改成你自己的。
"""

import os
import sys

# ===== 请修改这两处 =====
USERNAME = "YOUR_USERNAME"
REPO_DIR = "smart-agriculture-traceability"
# ========================

PROJECT_DIR = f"/home/{USERNAME}/{REPO_DIR}"
BACKEND_DIR = os.path.join(PROJECT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.chdir(BACKEND_DIR)

# config.py 会自动读取 backend/.env 中的数据库配置
from app import app as application  # noqa: E402
