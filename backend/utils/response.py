# -*- coding: utf-8 -*-
"""统一响应格式：成功 code=0；失败 code 为对应 HTTP 状态码。"""
from flask import jsonify


def ok(data=None, message="ok"):
    return jsonify({"code": 0, "message": message, "data": data})


def err(message, code=400):
    return jsonify({"code": code, "message": message}), code
