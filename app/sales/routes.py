from decimal import Decimal
from uuid import uuid4

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.sales import sales_bp
from app.sales.forms import CreateOrderForm, AddOrderItemForm, PaymentForm
from app.decorators import role_required
from app.extensions import db
from app.models.cafe_table import CafeTable
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem


def generate_order_code():
    return f"ORD{uuid4().hex[:8].upper()}"


def recalculate_order_total(order):
    total = sum(item.line_total for item in order.order_items) if order.order_items else Decimal("0")
    order.total_amount = total


def load_table_choices(form):
    query = CafeTable.query.filter_by(status="empty")

    if current_user.role and current_user.role.role_name in ["MANAGER", "STAFF"]:
        if current_user.employee:
            query = query.filter_by(store_id=current_user.employee.store_id)

    tables = query.order_by(CafeTable.store_id.asc(), CafeTable.table_code.asc()).all()

    form.table_id.choices = [
        (table.table_id, f"{table.store.store_code} - {table.table_code} ({table.capacity} chỗ)")
        for table in tables
    ]


def load_product_choices(form):
    products = Product.query.filter_by(status="available").order_by(Product.product_name.asc()).all()
    form.product_id.choices = [
        (product.product_id, f"{product.product_name} - {int(product.price):,} đ")
        for product in products
    ]


@sales_bp.route("/orders")
@login_required
@role_required("ADMIN", "MANAGER", "STAFF")
def orders_list():
    query = Order.query.order_by(Order.order_time.desc())

    if current_user.role and current_user.role.role_name in ["MANAGER", "STAFF"]:
        if current_user.employee:
            query = query.filter_by(store_id=current_user.employee.store_id)

    orders = query.all()
    return render_template("sales/orders_list.html", orders=orders)


@sales_bp.route("/orders/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER", "STAFF")
def create_order():
    if not current_user.employee:
        flash("Tài khoản này chưa gắn với nhân viên nên không thể tạo đơn hàng.", "danger")
        return redirect(url_for("main.dashboard"))

    form = CreateOrderForm()
    load_table_choices(form)

    if form.validate_on_submit():
        table = CafeTable.query.get_or_404(form.table_id.data)

        if table.status != "empty":
            flash("Bàn này không còn ở trạng thái trống.", "danger")
            return redirect(url_for("sales.create_order"))

        order = Order(
            order_code=generate_order_code(),
            store_id=table.store_id,
            table_id=table.table_id,
            employee_id=current_user.employee.employee_id,
            status="pending",
            total_amount=0,
            note=form.note.data.strip() if form.note.data else None
        )

        table.status = "occupied"

        db.session.add(order)
        db.session.commit()

        flash("Tạo đơn hàng thành công. Hãy thêm món vào đơn.", "success")
        return redirect(url_for("sales.order_detail", order_id=order.order_id))

    return render_template("sales/order_create.html", form=form)


@sales_bp.route("/orders/<int:order_id>")
@login_required
@role_required("ADMIN", "MANAGER", "STAFF")
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)

    if current_user.role and current_user.role.role_name in ["MANAGER", "STAFF"]:
        if current_user.employee and order.store_id != current_user.employee.store_id:
            flash("Bạn không có quyền xem đơn hàng này.", "danger")
            return redirect(url_for("sales.orders_list"))

    form = AddOrderItemForm()
    load_product_choices(form)

    return render_template("sales/order_detail.html", order=order, form=form)


@sales_bp.route("/orders/<int:order_id>/add-item", methods=["POST"])
@login_required
@role_required("ADMIN", "MANAGER", "STAFF")
def add_order_item(order_id):
    order = Order.query.get_or_404(order_id)

    if order.status != "pending":
        flash("Chỉ có thể thêm món vào đơn đang chờ thanh toán.", "danger")
        return redirect(url_for("sales.order_detail", order_id=order.order_id))

    if current_user.role and current_user.role.role_name in ["MANAGER", "STAFF"]:
        if current_user.employee and order.store_id != current_user.employee.store_id:
            flash("Bạn không có quyền thao tác đơn hàng này.", "danger")
            return redirect(url_for("sales.orders_list"))

    form = AddOrderItemForm()
    load_product_choices(form)

    if form.validate_on_submit():
        product = Product.query.get_or_404(form.product_id.data)

        if product.status != "available":
            flash("Sản phẩm này hiện không còn bán.", "danger")
            return redirect(url_for("sales.order_detail", order_id=order.order_id))

        quantity = form.quantity.data
        unit_price = Decimal(product.price)
        line_total = unit_price * quantity

        item = OrderItem(
            order_id=order.order_id,
            product_id=product.product_id,
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total,
            note=form.note.data.strip() if form.note.data else None
        )

        db.session.add(item)
        db.session.flush()

        recalculate_order_total(order)
        db.session.commit()

        flash("Thêm món thành công.", "success")
    else:
        flash("Dữ liệu món không hợp lệ.", "danger")

    return redirect(url_for("sales.order_detail", order_id=order.order_id))


@sales_bp.route("/orders/<int:order_id>/items/<int:item_id>/delete", methods=["POST"])
@login_required
@role_required("ADMIN", "MANAGER", "STAFF")
def delete_order_item(order_id, item_id):
    order = Order.query.get_or_404(order_id)
    item = OrderItem.query.get_or_404(item_id)

    if item.order_id != order.order_id:
        flash("Dòng món không thuộc đơn hàng này.", "danger")
        return redirect(url_for("sales.order_detail", order_id=order.order_id))

    if order.status != "pending":
        flash("Không thể xóa món của đơn đã thanh toán.", "danger")
        return redirect(url_for("sales.order_detail", order_id=order.order_id))

    db.session.delete(item)
    db.session.flush()

    recalculate_order_total(order)
    db.session.commit()

    flash("Xóa món thành công.", "success")
    return redirect(url_for("sales.order_detail", order_id=order.order_id))


@sales_bp.route("/orders/<int:order_id>/payment", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER", "STAFF")
def payment(order_id):
    order = Order.query.get_or_404(order_id)

    if order.status != "pending":
        flash("Đơn hàng này không ở trạng thái chờ thanh toán.", "danger")
        return redirect(url_for("sales.orders_list"))

    if not order.order_items:
        flash("Đơn hàng chưa có món nào, không thể thanh toán.", "danger")
        return redirect(url_for("sales.order_detail", order_id=order.order_id))

    form = PaymentForm()

    if form.validate_on_submit():
        recalculate_order_total(order)
        order.status = "paid"
        order.payment_method = form.payment_method.data
        order.table.status = "empty"

        db.session.commit()

        flash("Thanh toán thành công.", "success")
        return redirect(url_for("sales.orders_list"))

    return render_template("sales/payment.html", order=order, form=form)