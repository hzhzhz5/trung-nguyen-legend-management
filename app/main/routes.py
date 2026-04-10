from datetime import date

from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func

from app.main import main_bp
from app.extensions import db
from app.models.store import Store
from app.models.employee import Employee
from app.models.product import Product
from app.models.order import Order


def get_current_store_id():
    if current_user.employee:
        return current_user.employee.store_id
    return None


@main_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    today = date.today()
    current_store_id = get_current_store_id()
    role_name = current_user.role.role_name if current_user.role else None

    total_stores = Store.query.count()
    total_employees = Employee.query.count()
    total_products = Product.query.count()

    orders_today_query = Order.query.filter(func.date(Order.order_time) == today)
    revenue_today_query = db.session.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        Order.status == "paid",
        func.date(Order.order_time) == today
    )
    pending_orders_query = Order.query.filter(Order.status == "pending")

    if role_name in ["MANAGER", "STAFF"] and current_store_id:
        orders_today_query = orders_today_query.filter(Order.store_id == current_store_id)
        revenue_today_query = revenue_today_query.filter(Order.store_id == current_store_id)
        pending_orders_query = pending_orders_query.filter(Order.store_id == current_store_id)

    orders_today = orders_today_query.count()
    revenue_today = revenue_today_query.scalar()
    pending_orders = pending_orders_query.count()

    return render_template(
        "main/dashboard.html",
        total_stores=total_stores,
        total_employees=total_employees,
        total_products=total_products,
        orders_today=orders_today,
        revenue_today=revenue_today,
        pending_orders=pending_orders,
        role_name=role_name
    )