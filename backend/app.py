# -*- coding: utf-8 -*-
"""应用入口：Flask 应用工厂。"""
from flask import Flask

from config import Config
from extensions import cors, db


def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config.from_object(Config)

    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from routes.auth import auth_bp
    from routes.batches import batches_bp
    from routes.categories import categories_bp
    from routes.dashboard import dashboard_bp
    from routes.products import products_bp
    from routes.records import records_bp
    from routes.trace import trace_bp
    from routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(categories_bp, url_prefix="/api/categories")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(batches_bp, url_prefix="/api/batches")
    app.register_blueprint(records_bp)
    app.register_blueprint(trace_bp, url_prefix="/api/trace")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")

    @app.route("/api/health")
    def health():
        return {"code": 0, "message": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
