from datetime import date

from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from app.reports import reports_bp
from app.decorators import role_required
from app.extensions import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.store import Store


def get_current_store_id():
    if current_user.employee:
        return current_user.employee.store_id
    return None


@reports_bp.route("/revenue")
@login_required
@role_required("ADMIN", "MANAGER")
def revenue_report():
    today = date.today()
    current_store_id = get_current_store_id()
    is_manager = current_user.role and current_user.role.role_name == "MANAGER"

    # =========================
    # TÓM TẮT DOANH THU HÔM NAY
    # =========================
    paid_today_query = Order.query.filter(
        Order.status == "paid",
        func.date(Order.order_time) == today
    )

    if is_manager and current_store_id:
        paid_today_query = paid_today_query.filter(Order.store_id == current_store_id)

    paid_orders_today = paid_today_query.count()

    revenue_today = db.session.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        Order.status == "paid",
        func.date(Order.order_time) == today
    )

    if is_manager and current_store_id:
        revenue_today = revenue_today.filter(Order.store_id == current_store_id)

    revenue_today = revenue_today.scalar()

    # =========================
    # TỔNG ĐƠN ĐÃ THANH TOÁN
    # =========================
    paid_orders_query = Order.query.filter(Order.status == "paid")

    if is_manager and current_store_id:
        paid_orders_query = paid_orders_query.filter(Order.store_id == current_store_id)

    total_paid_orders = paid_orders_query.count()

    total_revenue_query = db.session.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(Order.status == "paid")

    if is_manager and current_store_id:
        total_revenue_query = total_revenue_query.filter(Order.store_id == current_store_id)

    total_revenue = total_revenue_query.scalar()

    # =========================
    # DOANH THU THEO CỬA HÀNG
    # =========================
    revenue_by_store_query = db.session.query(
        Store.store_name,
        func.coalesce(func.sum(Order.total_amount), 0).label("revenue"),
        func.count(Order.order_id).label("paid_orders")
    ).join(
        Order, Order.store_id == Store.store_id
    ).filter(
        Order.status == "paid"
    ).group_by(
        Store.store_id, Store.store_name
    ).order_by(
        func.coalesce(func.sum(Order.total_amount), 0).desc()
    )

    if is_manager and current_store_id:
        revenue_by_store_query = revenue_by_store_query.filter(Store.store_id == current_store_id)

    revenue_by_store = revenue_by_store_query.all()

    # =========================
    # TOP SẢN PHẨM BÁN CHẠY
    # =========================
    top_products_query = db.session.query(
        Product.product_name,
        func.coalesce(func.sum(OrderItem.quantity), 0).label("total_quantity"),
        func.coalesce(func.sum(OrderItem.line_total), 0).label("total_revenue")
    ).join(
        OrderItem, Product.product_id == OrderItem.product_id
    ).join(
        Order, Order.order_id == OrderItem.order_id
    ).filter(
        Order.status == "paid"
    ).group_by(
        Product.product_id, Product.product_name
    ).order_by(
        func.coalesce(func.sum(OrderItem.quantity), 0).desc()
    )

    if is_manager and current_store_id:
        top_products_query = top_products_query.filter(Order.store_id == current_store_id)

    top_products = top_products_query.limit(10).all()

    return render_template(
        "reports/revenue.html",
        revenue_today=revenue_today,
        paid_orders_today=paid_orders_today,
        total_paid_orders=total_paid_orders,
        total_revenue=total_revenue,
        revenue_by_store=revenue_by_store,
        top_products=top_products,
        is_manager=is_manager
    )