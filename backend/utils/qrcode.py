# -*- coding: utf-8 -*-
"""溯源码与二维码生成。"""
import os
import random
import string
import time

import qrcode
from flask import current_app


def generate_trace_code():
    """生成唯一溯源码：TR + 时间戳 + 6 位随机字符。"""
    ts = time.strftime("%Y%m%d%H%M%S")
    rand = "".join(random.choices(string.digits + string.ascii_uppercase, k=6))
    return f"TR{ts}{rand}"


def generate_qrcode(trace_code):
    """为溯源码生成二维码图片，返回可访问的相对路径。"""
    qr_dir = current_app.config["QR_DIR"]
    os.makedirs(qr_dir, exist_ok=True)

    filename = f"{trace_code}.png"
    content = f"{current_app.config['TRACE_PAGE_PREFIX']}{trace_code}"

    img = qrcode.make(content)
    img.save(os.path.join(qr_dir, filename))
    return f"/static/qrcodes/{filename}"
