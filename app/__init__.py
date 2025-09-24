from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from app.extensions import db
from .config import Config
from app.models import SiteUser
from .routes import register_blueprints
from .auth_client import login as auth_login, userinfo as auth_userinfo, auth_service_request
import logging, os, time, json
from logging import StreamHandler

def configure_logging():
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    root = logging.getLogger()
    root.setLevel(level)
    if not any(isinstance(h, StreamHandler) for h in root.handlers):
        root.addHandler(StreamHandler())

login_manager = LoginManager()

class ScriptNameFromForwardedPrefix:
    def __init__(self, app): self.app = app
    def __call__(self, environ, start_response):
        prefix = environ.get("HTTP_X_FORWARDED_PREFIX") or environ.get("HTTP_X_SCRIPT_NAME")
        if prefix:
            environ["SCRIPT_NAME"] = prefix.rstrip("/")
        return self.app(environ, start_response)

def create_app():
    configure_logging()
    app = Flask(__name__)
    app.config.from_object(Config)

    # prefix/proxy handling (for /bones)
    app.wsgi_app = ScriptNameFromForwardedPrefix(app.wsgi_app)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    @login_manager.user_loader
    def load_user(user_id):
        return SiteUser.query.get(int(user_id))

    register_blueprints(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app


def bootstrap_defaults(app):
    """Run once (master) before workers fork: create schema, ensure admin exists in auth-service and locally."""
    from sqlalchemy.exc import OperationalError
    from time import sleep

    with app.app_context():
        # wait for DB a bit
        for _ in range(12):
            try:
                db.session.execute(db.text("SELECT 1"))
                break
            except OperationalError:
                sleep(2)
        db.create_all()

        # ensure we can talk to auth-service
        api_key = app.config.get("AUTH_SERVICE_API_KEY")
        if not api_key:
            raise RuntimeError("AUTH_SERVICE_API_KEY is not set")

        username = f"{app.config.get('SITE_NAME','site')}_admin"
        password = app.config["SITE_ADMIN_PASSWORD"]

        # try login; if fails, register then login
        data, status = auth_login(username, password)
        if status != 200:
            reg_data, reg_status = auth_service_request("/register", {"username": username, "password": password})
            if reg_status in (200, 201, 400):  # 400 if already exists
                data, status = auth_login(username, password)

        if status == 200 and data:
            token = data["token"]
            info, s2 = auth_userinfo(token)
            if s2 == 200 and info:
                auth_user_id = info["id"]
                su = SiteUser.query.filter_by(auth_user_id=auth_user_id).first()
                if not su:
                    su = SiteUser(auth_user_id=auth_user_id,
                                  username=info.get("username") or username,
                                  email=info.get("email"),
                                  role="admin")
                    db.session.add(su)
                    db.session.commit()
                    logging.getLogger("bootstrap").info("bones_admin_linked", extra={"auth_user_id": auth_user_id})
        else:
            logging.getLogger("bootstrap").warning("bones_auth_setup_failed")
