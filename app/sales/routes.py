from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from flask import render_template, redirect, url_for, flash, request
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
    subtotal = sum(item.line_total for item in order.order_items) if order.order_items else Decimal("0")
    shipping_fee = Decimal("0")

    if getattr(order, "order_type", "dine_in") == "delivery":
        shipping_fee = subtotal * Decimal("0.05")

    order.subtotal = subtotal
    order.shipping_fee = shipping_fee
    order.total_amount = subtotal + shipping_fee


def can_access_order(order):
    if not current_user.role:
        return False

    role_name = current_user.role.role_name

    if role_name == "ADMIN":
        return True

    if role_name in ["MANAGER", "STAFF"]:
        if not current_user.employee:
            return False
        return order.store_id == current_user.employee.store_id

    return False


def load_table_choices(form):
    form.table_id.choices = [(0, "-- Chọn bàn --")]

    if not current_user.employee:
        return

    tables = (
        CafeTable.query.filter_by(store_id=current_user.employee.store_id)
        .order_by(CafeTable.table_code.asc())
        .all()
    )

    for table in tables:
        status_text = "Trống" if table.status == "empty" else "Đang sử dụng"
        form.table_id.choices.append(
            (table.table_id, f"{table.table_code} ({table.capacity} chỗ) - {status_text}")
        )


def load_product_choices(form):
    products = Product.query.filter_by(status="available").order_by(Product.product_name.asc()).all()
    form.product_id.choices = [
        (
            product.product_id,
            f"{product.product_name} - {int(product.price):,} đ - Còn: {getattr(product, 'quantity_in_stock', 0)}"
        )
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

    status = request.args.get("status")
    if status in ["pending", "paid", "cleared"]:
        query = query.filter_by(status=status)
    else:
        query = query.filter(Order.status.in_(["pending", "paid"]))

    orders = query.all()
    return render_template("sales/orders_list.html", orders=orders, current_status=status)


@sales_bp.route("/orders/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER", "STAFF")
def create_order():
    if not current_user.employee:
        flash("Tài khoản này chưa gắn với nhân viên nên không thể tạo đơn hàng.", "danger")
        return redirect(url_for("main.dashboard"))

    form = CreateOrderForm()
    load_table_choices(form)
    load_product_choices(form)

    tables = (
        CafeTable.query.filter_by(store_id=current_user.employee.store_id)
        .order_by(CafeTable.table_code.asc())
        .all()
    )

    if form.validate_on_submit():
        employee = current_user.employee
        order_type = form.order_type.data
        table = None

        customer_name = form.customer_name.data.strip() if form.customer_name.data else None
        customer_phone = form.customer_phone.data.strip() if form.customer_phone.data else None
        delivery_address = form.delivery_address.data.strip() if form.delivery_address.data else None
        note = form.note.data.strip() if form.note.data else None
        item_note = form.item_note.data.strip() if form.item_note.data else None

        if order_type == "dine_in":
            if not form.table_id.data or form.table_id.data == 0:
                flash("Vui lòng chọn bàn cho khách ngồi tại quán.", "danger")
                return render_template("sales/order_create.html", form=form, tables=tables)

            table = CafeTable.query.get_or_404(form.table_id.data)

            if table.store_id != employee.store_id:
                flash("Bạn không thể tạo đơn cho bàn ở cửa hàng khác.", "danger")
                return redirect(url_for("sales.create_order"))

            if table.status != "empty":
                flash("Bàn này không còn ở trạng thái trống.", "danger")
                return redirect(url_for("sales.create_order"))

        elif order_type == "takeaway":
            if not customer_name:
                flash("Đơn mang về cần nhập tên khách.", "danger")
                return render_template("sales/order_create.html", form=form, tables=tables)

        elif order_type == "delivery":
            if not customer_name:
                flash("Đơn ship cần nhập tên khách.", "danger")
                return render_template("sales/order_create.html", form=form, tables=tables)
            if not customer_phone:
                flash("Đơn ship cần nhập số điện thoại.", "danger")
                return render_template("sales/order_create.html", form=form, tables=tables)
            if not delivery_address:
                flash("Đơn ship cần nhập địa chỉ.", "danger")
                return render_template("sales/order_create.html", form=form, tables=tables)

        product = Product.query.get_or_404(form.product_id.data)

        if product.status != "available":
            flash("Sản phẩm này hiện không còn bán.", "danger")
            return render_template("sales/order_create.html", form=form, tables=tables)

        quantity = form.quantity.data
        quantity_in_stock = getattr(product, "quantity_in_stock", 0)

        if quantity_in_stock < quantity:
            flash("Số lượng tồn không đủ.", "danger")
            return render_template("sales/order_create.html", form=form, tables=tables)

        order = Order(
            order_code=generate_order_code(),
            store_id=employee.store_id,
            table_id=table.table_id if table else None,
            employee_id=employee.employee_id,
            order_type=order_type,
            customer_name=customer_name,
            customer_phone=customer_phone,
            delivery_address=delivery_address,
            status="pending",
            subtotal=Decimal("0"),
            shipping_fee=Decimal("0"),
            total_amount=Decimal("0"),
            note=note
        )

        db.session.add(order)
        db.session.flush()

        unit_price = Decimal(product.price)
        line_total = unit_price * quantity

        item = OrderItem(
            order_id=order.order_id,
            product_id=product.product_id,
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total,
            note=item_note
        )

        db.session.add(item)

        product.quantity_in_stock = quantity_in_stock - quantity

        if order.order_type == "dine_in" and order.table:
            order.table.status = "occupied"

        db.session.flush()
        recalculate_order_total(order)
        db.session.commit()

        flash("Tạo đơn hàng thành công.", "success")
        return redirect(url_for("sales.order_detail", order_id=order.order_id))

    return render_template("sales/order_create.html", form=form, tables=tables)

@sales_bp.route("/orders/<int:order_id>")
@login_required
@role_required("ADMIN", "MANAGER", "STAFF")
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)

    if not can_access_order(order):
        flash("Bạn không có quyền xem đơn hàng này.", "danger")
        return redirect(url_for("sales.orders_list"))

    form = AddOrderItemForm()
    load_product_choices(form)

    products = Product.query.filter_by(status="available").order_by(Product.product_name.asc()).all()

    category_names = []
    seen = set()

    for product in products:
        category_name = ""
        if hasattr(product, "category") and product.category:
            category_name = product.category.category_name or ""

        if category_name and category_name not in seen:
            seen.add(category_name)
            category_names.append(category_name)

    return render_template(
        "sales/order_detail.html",
        order=order,
        form=form,
        products=products,
        category_names=category_names,
    )

@sales_bp.route("/orders/<int:order_id>/add-item", methods=["POST"])
@login_required
@role_required("ADMIN", "MANAGER", "STAFF")
def add_order_item(order_id):
    order = Order.query.get_or_404(order_id)

    if not can_access_order(order):
        flash("Bạn không có quyền thao tác đơn hàng này.", "danger")
        return redirect(url_for("sales.orders_list"))

    if order.status != "pending":
        flash("Chỉ có thể thêm món vào đơn đang chờ thanh toán.", "danger")
        return redirect(url_for("sales.order_detail", order_id=order.order_id))

    form = AddOrderItemForm()
    load_product_choices(form)

    if form.validate_on_submit():
        product = Product.query.get_or_404(form.product_id.data)

        if product.status != "available":
            flash("Sản phẩm này hiện không còn bán.", "danger")
            return redirect(url_for("sales.order_detail", order_id=order.order_id))

        quantity = form.quantity.data
        quantity_in_stock = getattr(product, "quantity_in_stock", 0)

        if quantity_in_stock < quantity:
            flash("Số lượng tồn không đủ.", "danger")
            return redirect(url_for("sales.order_detail", order_id=order.order_id))

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

        product.quantity_in_stock = quantity_in_stock - quantity

        if order.order_type == "dine_in" and order.table:
            order.table.status = "occupied"

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

    if not can_access_order(order):
        flash("Bạn không có quyền thao tác đơn hàng này.", "danger")
        return redirect(url_for("sales.orders_list"))

    if order.status != "pending":
        flash("Không thể xóa món của đơn đã thanh toán.", "danger")
        return redirect(url_for("sales.order_detail", order_id=order.order_id))

    if item.product and hasattr(item.product, "quantity_in_stock"):
        item.product.quantity_in_stock = (item.product.quantity_in_stock or 0) + item.quantity

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

    if not can_access_order(order):
        flash("Bạn không có quyền thao tác đơn hàng này.", "danger")
        return redirect(url_for("sales.orders_list"))

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

        # không trả bàn ở bước thanh toán nữa

        db.session.commit()

        flash("Thanh toán thành công.", "success")
        return redirect(url_for("sales.orders_list"))

    return render_template("sales/payment.html", order=order, form=form)


@sales_bp.route("/orders/<int:order_id>/clear-table", methods=["POST"])
@login_required
@role_required("ADMIN", "MANAGER", "STAFF")
def clear_table(order_id):
    order = Order.query.get_or_404(order_id)

    if not can_access_order(order):
        flash("Bạn không có quyền thao tác đơn hàng này.", "danger")
        return redirect(url_for("sales.orders_list"))

    if order.order_type != "dine_in":
        flash("Chỉ đơn tại quán mới có thao tác dọn bàn.", "danger")
        return redirect(url_for("sales.orders_list"))

    if order.status != "paid":
        flash("Chỉ được dọn bàn sau khi đơn đã thanh toán.", "danger")
        return redirect(url_for("sales.orders_list"))

    if order.table:
        order.table.status = "empty"

    order.status = "cleared"
    order.cleared_at = datetime.utcnow()

    db.session.commit()

    flash("Dọn bàn thành công.", "success")
    return redirect(url_for("sales.orders_list"))