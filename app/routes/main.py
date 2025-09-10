from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import SiteUser
from app.auth_client import login as auth_login, userinfo as auth_userinfo

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("routes/main/index.html")

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 1. Authenticate against auth service
        login_data, status = auth_login(username, password)
        if status != 200 or not login_data.get("token"):
            flash("Invalid credentials", "danger")
            return redirect(url_for("main.login"))

        token = login_data["token"]
        session["auth_token"] = token

        # 2. Fetch user info
        info, status = auth_userinfo(token)
        if status != 200:
            flash("Failed to fetch user info", "danger")
            return redirect(url_for("main.login"))

        # 3. Ensure user exists locally
        site_user = SiteUser.query.filter_by(auth_user_id=info["id"]).first()
        if not site_user:
            site_user = SiteUser(
                auth_user_id=info["id"],
                username=info["username"],
                email=info.get("email"),
                role="user"  # default role
            )
            db.session.add(site_user)
            db.session.commit()
            flash(f"Welcome {info['username']}! Your account was provisioned.", "success")

        # 4. Login with Flask-Login
        login_user(site_user)
        return redirect(url_for("main.index"))

    return render_template("routes/main/login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("auth_token", None)
    return redirect(url_for("main.index"))
