from functools import wraps

from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from database.models import User


admin_auth_bp = Blueprint("admin_auth", __name__, url_prefix="/admin")


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("admin_auth.login"))

        if not current_user.is_admin or not current_user.is_active:
            abort(403)

        return view(*args, **kwargs)

    return wrapped_view


@admin_auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and current_user.is_admin and current_user.is_active:
        return redirect(url_for("admin_dashboard"))

    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if (
            user
            and user.is_admin
            and user.is_active
            and check_password_hash(user.password_hash, password)
        ):
            login_user(user)
            return redirect(url_for("admin_dashboard"))

        error = "Неверный email или пароль."

    return render_template("admin/login.html", error=error, lang="ru")


@admin_auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin_auth.login"))
