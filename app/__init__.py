from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Vui lòng đăng nhập để tiếp tục."
    login_manager.login_message_category = "warning"

    from app import models
    from app.models.user_account import UserAccount

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(UserAccount, int(user_id))

    from app.auth import auth_bp
    from app.main import main_bp
    from app.admin import admin_bp
    from app.sales import sales_bp
    from app.inventory import inventory_bp
    from app.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(sales_bp, url_prefix="/sales")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    from app.catalog import catalog_bp

    app.register_blueprint(catalog_bp, url_prefix="/catalog")

    return app