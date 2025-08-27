from flask import Blueprint, render_template, session, redirect, url_for, flash
from ..auth_client import userinfo as auth_userinfo
import markdown

bp = Blueprint("readme", __name__, template_folder="../templates/routes/readme")

@bp.route("/readme")
def readme():
    if "token" not in session:
        flash("Please log in")
        return redirect(url_for("main.login"))

    data, status = auth_userinfo(session["token"])
    if status != 200:
        flash("Invalid session")
        return redirect(url_for("main.login"))

    with open("USER-README.md") as f:
        content = markdown.markdown(f.read())

    return render_template("routes/readme/readme.html", content=content)
