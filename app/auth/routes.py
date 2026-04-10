from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required

from app.auth import auth_bp
from app.auth.forms import LoginForm
from app.models.user_account import UserAccount

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        user = UserAccount.query.filter_by(username=username).first()

        if user and user.status == "active" and user.check_password(password):
            login_user(user)
            flash("Đăng nhập thành công.", "success")

            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))
        else:
            flash("Sai tên đăng nhập hoặc mật khẩu.", "danger")

    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for("auth.login"))