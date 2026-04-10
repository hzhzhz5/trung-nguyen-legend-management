from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required

def role_required(*allowed_roles):
    def decorator(func):
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role is None:
                flash("Tài khoản chưa được gán vai trò.", "danger")
                return redirect(url_for("main.dashboard"))

            if current_user.role.role_name not in allowed_roles:
                flash("Bạn không có quyền truy cập chức năng này.", "danger")
                return redirect(url_for("main.dashboard"))

            return func(*args, **kwargs)
        return wrapper
    return decorator