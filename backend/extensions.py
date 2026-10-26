# -*- coding: utf-8 -*-
"""共享扩展实例，避免循环导入。"""
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()
cors = CORS()
