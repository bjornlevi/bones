from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, SiteUser

bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="../templates/routes/admin")

@bp.route("/")
@login_required
def dashboard():
    if current_user.role != "admin":
        return "Forbidden", 403
    return render_template("routes/admin/dashboard.html")

@bp.route("/users")
@login_required
def list_users():
    if current_user.role != "admin":
        return "Forbidden", 403
    users = SiteUser.query.all()
    return render_template("routes/admin/admin_users.html", users=users)

@bp.route("/users/toggle/<int:user_id>", methods=["POST"])
@login_required
def toggle_admin(user_id):
    if current_user.role != "admin":
        return "Forbidden", 403
    user = SiteUser.query.get(user_id)
    if not user:
        flash("User not found", "danger")
    else:
        user.role = "admin" if user.role != "admin" else "user"
        db.session.commit()
        flash(f"{user.username} role changed to {user.role}", "success")
    return redirect(url_for("admin.list_users"))
