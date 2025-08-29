from flask import Flask
from flask_login import LoginManager
from .config import Config
from .models import db, SiteUser
from .routes import register_blueprints
from .auth_client import login as auth_login, userinfo as auth_userinfo, auth_service_request
import os

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"   # adjust if your login route is elsewhere

    @login_manager.user_loader
    def load_user(user_id):
        return SiteUser.query.get(int(user_id))

    # Make SITE_NAME available in all templates
    app.jinja_env.globals["SITE_NAME"] = app.config.get("SITE_NAME", "site")

    with app.app_context():
        db.create_all()

        if not app.config.get("AUTH_SERVICE_API_KEY"):
            raise RuntimeError("[BOOTSTRAP ERROR] AUTH_SERVICE_API_KEY is not set in environment")

        username = f"{app.config.get('SITE_NAME', 'site')}_admin"
        password = app.config["SITE_ADMIN_PASSWORD"]

        # ✅ Step 1: Try login first
        data, status = auth_login(username, password)

        if status != 200:
            # ✅ Step 2: Try register
            reg_data, reg_status = auth_service_request(
                "/register",
                {"username": username, "password": password}
            )
            if reg_status == 201:
                print(f"[BOOTSTRAP] Created {username} on auth service")
                data, status = auth_login(username, password)
            elif reg_status == 400:
                print(f"[BOOTSTRAP] {username} already exists on auth service")
                data, status = auth_login(username, password)

        if status == 200 and data:
            token = data["token"]
            info, status = auth_userinfo(token)
            if status == 200 and info:
                auth_user_id = info["id"]

                site_user = SiteUser.query.filter_by(auth_user_id=auth_user_id).first()
                if not site_user:
                    db.session.add(
                        SiteUser(
                            auth_user_id=auth_user_id,
                            username=info["username"],   # ✅ populate username
                            email=info.get("email"),     # ✅ if provided
                            role="admin"
                        )
                    )
                    db.session.commit()
                    print(f"[BOOTSTRAP] {info['username']} linked to auth_user_id={auth_user_id} with local admin role")
        else:
            print(f"[BOOTSTRAP WARNING] Could not create or login {username} on auth service")


    register_blueprints(app)
    return app
