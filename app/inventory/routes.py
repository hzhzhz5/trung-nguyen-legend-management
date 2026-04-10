from decimal import Decimal
from uuid import uuid4

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.inventory import inventory_bp
from app.inventory.forms import (
    IngredientForm,
    SupplierForm,
    CreatePurchaseOrderForm,
    AddPurchaseOrderItemForm,
    ConfirmReceiveForm,
)
from app.decorators import role_required
from app.extensions import db
from app.models.store import Store
from app.models.ingredient import Ingredient
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.store_inventory import StoreInventory
from app.models.inventory_transaction import InventoryTransaction


def generate_purchase_order_code():
    return f"PO{uuid4().hex[:8].upper()}"


def recalculate_purchase_order_total(purchase_order):
    total = sum(item.line_total for item in purchase_order.items) if purchase_order.items else Decimal("0")
    purchase_order.total_amount = total


def load_store_choices(form):
    if current_user.role and current_user.role.role_name == "MANAGER":
        if not current_user.employee:
            form.store_id.choices = []
            return

        store = current_user.employee.store
        form.store_id.choices = [
            (store.store_id, f"{store.store_code} - {store.store_name}")
        ]
    else:
        stores = Store.query.order_by(Store.store_name.asc()).all()
        form.store_id.choices = [
            (store.store_id, f"{store.store_code} - {store.store_name}")
            for store in stores
        ]


def load_supplier_choices(form):
    suppliers = Supplier.query.filter_by(status="active").order_by(Supplier.supplier_name.asc()).all()
    form.supplier_id.choices = [
        (supplier.supplier_id, f"{supplier.supplier_code} - {supplier.supplier_name}")
        for supplier in suppliers
    ]


def load_ingredient_choices(form):
    ingredients = Ingredient.query.filter_by(status="active").order_by(Ingredient.ingredient_name.asc()).all()
    form.ingredient_id.choices = [
        (ingredient.ingredient_id, f"{ingredient.ingredient_name} ({ingredient.unit})")
        for ingredient in ingredients
    ]


# =========================
# INGREDIENT ROUTES
# =========================

@inventory_bp.route("/ingredients")
@login_required
@role_required("ADMIN", "MANAGER")
def ingredients_list():
    ingredients = Ingredient.query.order_by(Ingredient.ingredient_id.desc()).all()
    return render_template("inventory/ingredients_list.html", ingredients=ingredients)


@inventory_bp.route("/ingredients/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def create_ingredient():
    form = IngredientForm()

    if form.validate_on_submit():
        existing_ingredient = Ingredient.query.filter_by(
            ingredient_code=form.ingredient_code.data.strip()
        ).first()

        if existing_ingredient:
            flash("Mã nguyên liệu đã tồn tại.", "danger")
            return render_template("inventory/ingredient_form.html", form=form, title="Thêm nguyên liệu")

        ingredient = Ingredient(
            ingredient_code=form.ingredient_code.data.strip(),
            ingredient_name=form.ingredient_name.data.strip(),
            unit=form.unit.data.strip(),
            min_stock_level=form.min_stock_level.data,
            status=form.status.data
        )

        db.session.add(ingredient)
        db.session.commit()

        flash("Thêm nguyên liệu thành công.", "success")
        return redirect(url_for("inventory.ingredients_list"))

    return render_template("inventory/ingredient_form.html", form=form, title="Thêm nguyên liệu")


@inventory_bp.route("/ingredients/<int:ingredient_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def edit_ingredient(ingredient_id):
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    form = IngredientForm(obj=ingredient)

    if form.validate_on_submit():
        existing_ingredient = Ingredient.query.filter(
            Ingredient.ingredient_code == form.ingredient_code.data.strip(),
            Ingredient.ingredient_id != ingredient.ingredient_id
        ).first()

        if existing_ingredient:
            flash("Mã nguyên liệu đã tồn tại ở nguyên liệu khác.", "danger")
            return render_template("inventory/ingredient_form.html", form=form, title="Sửa nguyên liệu")

        ingredient.ingredient_code = form.ingredient_code.data.strip()
        ingredient.ingredient_name = form.ingredient_name.data.strip()
        ingredient.unit = form.unit.data.strip()
        ingredient.min_stock_level = form.min_stock_level.data
        ingredient.status = form.status.data

        db.session.commit()

        flash("Cập nhật nguyên liệu thành công.", "success")
        return redirect(url_for("inventory.ingredients_list"))

    return render_template("inventory/ingredient_form.html", form=form, title="Sửa nguyên liệu")


@inventory_bp.route("/ingredients/<int:ingredient_id>/delete", methods=["POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def delete_ingredient(ingredient_id):
    ingredient = Ingredient.query.get_or_404(ingredient_id)

    if ingredient.purchase_order_items or ingredient.inventory_records or ingredient.inventory_transactions:
        flash("Không thể xóa nguyên liệu đã phát sinh giao dịch hoặc tồn kho.", "danger")
        return redirect(url_for("inventory.ingredients_list"))

    db.session.delete(ingredient)
    db.session.commit()

    flash("Xóa nguyên liệu thành công.", "success")
    return redirect(url_for("inventory.ingredients_list"))


# =========================
# SUPPLIER ROUTES
# =========================

@inventory_bp.route("/suppliers")
@login_required
@role_required("ADMIN", "MANAGER")
def suppliers_list():
    suppliers = Supplier.query.order_by(Supplier.supplier_id.desc()).all()
    return render_template("inventory/suppliers_list.html", suppliers=suppliers)


@inventory_bp.route("/suppliers/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def create_supplier():
    form = SupplierForm()

    if form.validate_on_submit():
        existing_supplier = Supplier.query.filter_by(
            supplier_code=form.supplier_code.data.strip()
        ).first()

        if existing_supplier:
            flash("Mã nhà cung cấp đã tồn tại.", "danger")
            return render_template("inventory/supplier_form.html", form=form, title="Thêm nhà cung cấp")

        supplier = Supplier(
            supplier_code=form.supplier_code.data.strip(),
            supplier_name=form.supplier_name.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            email=form.email.data.strip() if form.email.data else None,
            address=form.address.data.strip() if form.address.data else None,
            status=form.status.data
        )

        db.session.add(supplier)
        db.session.commit()

        flash("Thêm nhà cung cấp thành công.", "success")
        return redirect(url_for("inventory.suppliers_list"))

    return render_template("inventory/supplier_form.html", form=form, title="Thêm nhà cung cấp")


@inventory_bp.route("/suppliers/<int:supplier_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def edit_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    form = SupplierForm(obj=supplier)

    if form.validate_on_submit():
        existing_supplier = Supplier.query.filter(
            Supplier.supplier_code == form.supplier_code.data.strip(),
            Supplier.supplier_id != supplier.supplier_id
        ).first()

        if existing_supplier:
            flash("Mã nhà cung cấp đã tồn tại ở nhà cung cấp khác.", "danger")
            return render_template("inventory/supplier_form.html", form=form, title="Sửa nhà cung cấp")

        supplier.supplier_code = form.supplier_code.data.strip()
        supplier.supplier_name = form.supplier_name.data.strip()
        supplier.phone = form.phone.data.strip() if form.phone.data else None
        supplier.email = form.email.data.strip() if form.email.data else None
        supplier.address = form.address.data.strip() if form.address.data else None
        supplier.status = form.status.data

        db.session.commit()

        flash("Cập nhật nhà cung cấp thành công.", "success")
        return redirect(url_for("inventory.suppliers_list"))

    return render_template("inventory/supplier_form.html", form=form, title="Sửa nhà cung cấp")


@inventory_bp.route("/suppliers/<int:supplier_id>/delete", methods=["POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)

    if supplier.purchase_orders:
        flash("Không thể xóa nhà cung cấp đã có phiếu nhập.", "danger")
        return redirect(url_for("inventory.suppliers_list"))

    db.session.delete(supplier)
    db.session.commit()

    flash("Xóa nhà cung cấp thành công.", "success")
    return redirect(url_for("inventory.suppliers_list"))


# =========================
# PURCHASE ORDER ROUTES
# =========================

@inventory_bp.route("/purchase-orders")
@login_required
@role_required("ADMIN", "MANAGER")
def purchase_orders_list():
    query = PurchaseOrder.query.order_by(PurchaseOrder.order_date.desc())

    if current_user.role and current_user.role.role_name == "MANAGER":
        if current_user.employee:
            query = query.filter_by(store_id=current_user.employee.store_id)

    purchase_orders = query.all()
    return render_template("inventory/purchase_orders_list.html", purchase_orders=purchase_orders)


@inventory_bp.route("/purchase-orders/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def create_purchase_order():
    form = CreatePurchaseOrderForm()
    load_supplier_choices(form)
    load_store_choices(form)

    if form.validate_on_submit():
        purchase_order = PurchaseOrder(
            purchase_order_code=generate_purchase_order_code(),
            supplier_id=form.supplier_id.data,
            store_id=form.store_id.data,
            created_by=current_user.employee.employee_id if current_user.employee else None,
            status="draft",
            total_amount=0,
            note=form.note.data.strip() if form.note.data else None
        )

        db.session.add(purchase_order)
        db.session.commit()

        flash("Tạo phiếu nhập thành công. Hãy thêm nguyên liệu vào phiếu.", "success")
        return redirect(url_for("inventory.purchase_order_detail", purchase_order_id=purchase_order.purchase_order_id))

    return render_template("inventory/purchase_order_form.html", form=form, title="Tạo phiếu nhập")


@inventory_bp.route("/purchase-orders/<int:purchase_order_id>")
@login_required
@role_required("ADMIN", "MANAGER")
def purchase_order_detail(purchase_order_id):
    purchase_order = PurchaseOrder.query.get_or_404(purchase_order_id)

    if current_user.role and current_user.role.role_name == "MANAGER":
        if current_user.employee and purchase_order.store_id != current_user.employee.store_id:
            flash("Bạn không có quyền xem phiếu nhập này.", "danger")
            return redirect(url_for("inventory.purchase_orders_list"))

    add_form = AddPurchaseOrderItemForm()
    load_ingredient_choices(add_form)
    confirm_form = ConfirmReceiveForm()

    return render_template(
        "inventory/purchase_order_detail.html",
        purchase_order=purchase_order,
        add_form=add_form,
        confirm_form=confirm_form
    )


@inventory_bp.route("/purchase-orders/<int:purchase_order_id>/add-item", methods=["POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def add_purchase_order_item(purchase_order_id):
    purchase_order = PurchaseOrder.query.get_or_404(purchase_order_id)

    if purchase_order.status != "draft":
        flash("Chỉ có thể thêm nguyên liệu vào phiếu nhập nháp.", "danger")
        return redirect(url_for("inventory.purchase_order_detail", purchase_order_id=purchase_order.purchase_order_id))

    if current_user.role and current_user.role.role_name == "MANAGER":
        if current_user.employee and purchase_order.store_id != current_user.employee.store_id:
            flash("Bạn không có quyền thao tác phiếu nhập này.", "danger")
            return redirect(url_for("inventory.purchase_orders_list"))

    form = AddPurchaseOrderItemForm()
    load_ingredient_choices(form)

    if form.validate_on_submit():
        ingredient = Ingredient.query.get_or_404(form.ingredient_id.data)

        quantity = Decimal(str(form.quantity.data))
        unit_price = Decimal(str(form.unit_price.data))
        line_total = quantity * unit_price

        item = PurchaseOrderItem(
            purchase_order_id=purchase_order.purchase_order_id,
            ingredient_id=ingredient.ingredient_id,
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total,
            note=form.note.data.strip() if form.note.data else None
        )

        db.session.add(item)
        db.session.flush()

        recalculate_purchase_order_total(purchase_order)
        db.session.commit()

        flash("Thêm nguyên liệu vào phiếu nhập thành công.", "success")
    else:
        flash("Dữ liệu nguyên liệu không hợp lệ.", "danger")

    return redirect(url_for("inventory.purchase_order_detail", purchase_order_id=purchase_order.purchase_order_id))


@inventory_bp.route("/purchase-orders/<int:purchase_order_id>/items/<int:item_id>/delete", methods=["POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def delete_purchase_order_item(purchase_order_id, item_id):
    purchase_order = PurchaseOrder.query.get_or_404(purchase_order_id)
    item = PurchaseOrderItem.query.get_or_404(item_id)

    if purchase_order.status != "draft":
        flash("Không thể xóa dòng nguyên liệu của phiếu đã hoàn tất.", "danger")
        return redirect(url_for("inventory.purchase_order_detail", purchase_order_id=purchase_order.purchase_order_id))

    if item.purchase_order_id != purchase_order.purchase_order_id:
        flash("Dòng nguyên liệu không thuộc phiếu nhập này.", "danger")
        return redirect(url_for("inventory.purchase_order_detail", purchase_order_id=purchase_order.purchase_order_id))

    db.session.delete(item)
    db.session.flush()

    recalculate_purchase_order_total(purchase_order)
    db.session.commit()

    flash("Xóa dòng nguyên liệu thành công.", "success")
    return redirect(url_for("inventory.purchase_order_detail", purchase_order_id=purchase_order.purchase_order_id))


@inventory_bp.route("/purchase-orders/<int:purchase_order_id>/complete", methods=["POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def complete_purchase_order(purchase_order_id):
    purchase_order = PurchaseOrder.query.get_or_404(purchase_order_id)
    form = ConfirmReceiveForm()

    if not form.validate_on_submit():
        flash("Yêu cầu xác nhận không hợp lệ.", "danger")
        return redirect(url_for("inventory.purchase_order_detail", purchase_order_id=purchase_order.purchase_order_id))

    if purchase_order.status != "draft":
        flash("Phiếu nhập này không còn ở trạng thái nháp.", "danger")
        return redirect(url_for("inventory.purchase_orders_list"))

    if not purchase_order.items:
        flash("Phiếu nhập chưa có nguyên liệu nào, không thể xác nhận nhập kho.", "danger")
        return redirect(url_for("inventory.purchase_order_detail", purchase_order_id=purchase_order.purchase_order_id))

    operator_employee_id = current_user.employee.employee_id if current_user.employee else purchase_order.created_by

    for item in purchase_order.items:
        inventory_record = StoreInventory.query.filter_by(
            store_id=purchase_order.store_id,
            ingredient_id=item.ingredient_id
        ).first()

        if not inventory_record:
            inventory_record = StoreInventory(
                store_id=purchase_order.store_id,
                ingredient_id=item.ingredient_id,
                quantity_on_hand=0
            )
            db.session.add(inventory_record)
            db.session.flush()

        inventory_record.quantity_on_hand = Decimal(str(inventory_record.quantity_on_hand or 0)) + Decimal(str(item.quantity))

        transaction = InventoryTransaction(
            store_id=purchase_order.store_id,
            ingredient_id=item.ingredient_id,
            transaction_type="IN",
            quantity=item.quantity,
            reference_type="PURCHASE_ORDER",
            reference_id=purchase_order.purchase_order_id,
            created_by=operator_employee_id,
            note=f"Nhập kho từ phiếu {purchase_order.purchase_order_code}"
        )
        db.session.add(transaction)

    recalculate_purchase_order_total(purchase_order)
    purchase_order.status = "completed"

    db.session.commit()

    flash("Xác nhận nhập kho thành công.", "success")
    return redirect(url_for("inventory.purchase_orders_list"))


# =========================
# INVENTORY VIEWS
# =========================

@inventory_bp.route("/stock")
@login_required
@role_required("ADMIN", "MANAGER")
def inventory_list():
    query = StoreInventory.query.order_by(StoreInventory.inventory_id.desc())

    if current_user.role and current_user.role.role_name == "MANAGER":
        if current_user.employee:
            query = query.filter_by(store_id=current_user.employee.store_id)

    inventory_records = query.all()
    return render_template("inventory/inventory_list.html", inventory_records=inventory_records)


@inventory_bp.route("/transactions")
@login_required
@role_required("ADMIN", "MANAGER")
def transactions_list():
    query = InventoryTransaction.query.order_by(InventoryTransaction.created_at.desc())

    if current_user.role and current_user.role.role_name == "MANAGER":
        if current_user.employee:
            query = query.filter_by(store_id=current_user.employee.store_id)

    transactions = query.all()
    return render_template("inventory/transactions_list.html", transactions=transactions)