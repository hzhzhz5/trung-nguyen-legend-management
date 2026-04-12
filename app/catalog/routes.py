from flask import render_template, redirect, url_for, flash, request
from sqlalchemy import func, desc
from flask_login import login_required

from app.catalog import catalog_bp
from app.catalog.forms import TableForm, CategoryForm, ProductForm
from app.decorators import role_required
from app.extensions import db
from app.models.store import Store
from app.models.cafe_table import CafeTable
from app.models.category import Category
from app.models.product import Product
from app.models import Product, Category, CafeTable, Order, OrderItem, Employee, Role


def load_store_choices(form):
    stores = Store.query.order_by(Store.store_name.asc()).all()
    form.store_id.choices = [
        (store.store_id, f"{store.store_code} - {store.store_name}")
        for store in stores
    ]


def load_category_choices(form):
    categories = Category.query.order_by(Category.category_name.asc()).all()
    form.category_id.choices = [
        (category.category_id, category.category_name)
        for category in categories
    ]


# =========================
# TABLE ROUTES
# =========================

@catalog_bp.route("/tables")
@login_required
@role_required("ADMIN", "MANAGER")
def tables_list():
    status_filter = request.args.get("status", "").strip()

    all_tables = CafeTable.query.order_by(CafeTable.table_code.asc()).all()

    empty_count = sum(1 for table in all_tables if table.status == "empty")
    occupied_count = sum(1 for table in all_tables if table.status == "occupied")
    unavailable_count = sum(1 for table in all_tables if table.status == "unavailable")
    total_count = len(all_tables)

    if status_filter in ["empty", "occupied", "unavailable"]:
        tables = [table for table in all_tables if table.status == status_filter]
    else:
        tables = all_tables
        status_filter = ""

    return render_template(
        "catalog/tables_list.html",
        tables=tables,
        total_count=total_count,
        empty_count=empty_count,
        occupied_count=occupied_count,
        unavailable_count=unavailable_count,
        current_filter=status_filter,
    )


@catalog_bp.route("/tables/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def create_table():
    form = TableForm()
    load_store_choices(form)

    if form.validate_on_submit():
        existing_table = CafeTable.query.filter_by(
            store_id=form.store_id.data,
            table_code=form.table_code.data.strip()
        ).first()

        if existing_table:
            flash("Mã bàn đã tồn tại trong cửa hàng này.", "danger")
            return render_template("catalog/table_form.html", form=form, title="Thêm bàn")

        table = CafeTable(
            store_id=form.store_id.data,
            table_code=form.table_code.data.strip(),
            capacity=form.capacity.data,
            status=form.status.data
        )

        db.session.add(table)
        db.session.commit()

        flash("Thêm bàn thành công.", "success")
        return redirect(url_for("catalog.tables_list"))

    return render_template("catalog/table_form.html", form=form, title="Thêm bàn")


@catalog_bp.route("/tables/<int:table_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def edit_table(table_id):
    table = CafeTable.query.get_or_404(table_id)
    form = TableForm(obj=table)
    load_store_choices(form)

    if form.validate_on_submit():
        existing_table = CafeTable.query.filter(
            CafeTable.store_id == form.store_id.data,
            CafeTable.table_code == form.table_code.data.strip(),
            CafeTable.table_id != table.table_id
        ).first()

        if existing_table:
            flash("Mã bàn đã tồn tại trong cửa hàng này.", "danger")
            return render_template("catalog/table_form.html", form=form, title="Sửa bàn")

        table.store_id = form.store_id.data
        table.table_code = form.table_code.data.strip()
        table.capacity = form.capacity.data
        table.status = form.status.data

        db.session.commit()

        flash("Cập nhật bàn thành công.", "success")
        return redirect(url_for("catalog.tables_list"))

    return render_template("catalog/table_form.html", form=form, title="Sửa bàn")


@catalog_bp.route("/tables/<int:table_id>/delete", methods=["POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def delete_table(table_id):
    table = CafeTable.query.get_or_404(table_id)

    if table.status == "occupied":
        flash("Không thể xóa bàn đang có khách.", "danger")
        return redirect(url_for("catalog.tables_list"))

    db.session.delete(table)
    db.session.commit()

    flash("Xóa bàn thành công.", "success")
    return redirect(url_for("catalog.tables_list"))


# =========================
# CATEGORY ROUTES
# =========================

@catalog_bp.route("/categories")
@login_required
@role_required("ADMIN", "MANAGER")
def categories_list():
    categories = Category.query.order_by(Category.category_id.desc()).all()
    return render_template("catalog/categories_list.html", categories=categories)


@catalog_bp.route("/categories/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def create_category():
    form = CategoryForm()

    if form.validate_on_submit():
        existing_category = Category.query.filter_by(
            category_name=form.category_name.data.strip()
        ).first()

        if existing_category:
            flash("Tên danh mục đã tồn tại.", "danger")
            return render_template("catalog/category_form.html", form=form, title="Thêm danh mục")

        category = Category(
            category_name=form.category_name.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            status=form.status.data
        )

        db.session.add(category)
        db.session.commit()

        flash("Thêm danh mục thành công.", "success")
        return redirect(url_for("catalog.categories_list"))

    return render_template("catalog/category_form.html", form=form, title="Thêm danh mục")


@catalog_bp.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        existing_category = Category.query.filter(
            Category.category_name == form.category_name.data.strip(),
            Category.category_id != category.category_id
        ).first()

        if existing_category:
            flash("Tên danh mục đã tồn tại ở danh mục khác.", "danger")
            return render_template("catalog/category_form.html", form=form, title="Sửa danh mục")

        category.category_name = form.category_name.data.strip()
        category.description = form.description.data.strip() if form.description.data else None
        category.status = form.status.data

        db.session.commit()

        flash("Cập nhật danh mục thành công.", "success")
        return redirect(url_for("catalog.categories_list"))

    return render_template("catalog/category_form.html", form=form, title="Sửa danh mục")


@catalog_bp.route("/categories/<int:category_id>/delete", methods=["POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    if category.products:
        flash("Không thể xóa danh mục đang có sản phẩm.", "danger")
        return redirect(url_for("catalog.categories_list"))

    db.session.delete(category)
    db.session.commit()

    flash("Xóa danh mục thành công.", "success")
    return redirect(url_for("catalog.categories_list"))


# =========================
# PRODUCT ROUTES
# =========================

@catalog_bp.route("/products")
@login_required
@role_required("ADMIN", "MANAGER")
def products_list():
    search = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", "").strip()
    sort_by = request.args.get("sort_by", "name").strip()

    sales_subquery = (
        db.session.query(
            OrderItem.product_id.label("product_id"),
            func.coalesce(func.sum(OrderItem.quantity), 0).label("sold_qty"),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0).label("revenue"),
        )
        .join(Order, Order.order_id == OrderItem.order_id)
        .filter(Order.status == "paid")
        .group_by(OrderItem.product_id)
        .subquery()
    )

    query = (
        db.session.query(
            Product,
            func.coalesce(sales_subquery.c.sold_qty, 0).label("sold_qty"),
            func.coalesce(sales_subquery.c.revenue, 0).label("revenue"),
        )
        .outerjoin(sales_subquery, Product.product_id == sales_subquery.c.product_id)
        .join(Category, Product.category_id == Category.category_id)
    )

    if search:
        query = query.filter(
            (Product.product_name.ilike(f"%{search}%")) |
            (Product.product_code.ilike(f"%{search}%"))
        )

    if category_id and category_id.isdigit():
        query = query.filter(Product.category_id == int(category_id))

    if sort_by == "name":
        query = query.order_by(Product.product_name.asc())
    elif sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "sold_desc":
        query = query.order_by(desc("sold_qty"), Product.product_name.asc())
    elif sort_by == "revenue_desc":
        query = query.order_by(desc("revenue"), Product.product_name.asc())
    else:
        query = query.order_by(Product.product_name.asc())

    products_raw = query.all()
    categories = Category.query.order_by(Category.category_name.asc()).all()

    products = []
    for product, sold_qty, revenue in products_raw:
        products.append({
            "product": product,
            "sold_qty": int(sold_qty or 0),
            "revenue": float(revenue or 0),
        })

    return render_template(
        "catalog/products_list.html",
        products=products,
        categories=categories,
        search=search,
        current_category=category_id,
        sort_by=sort_by,
    )

@catalog_bp.route("/products/<int:product_id>/stats")
@login_required
@role_required("ADMIN", "MANAGER")
def product_stats(product_id):
    product = Product.query.get_or_404(product_id)

    stats = (
        db.session.query(
            func.coalesce(func.sum(OrderItem.quantity), 0).label("sold_qty"),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0).label("revenue"),
        )
        .join(Order, Order.order_id == OrderItem.order_id)
        .filter(
            OrderItem.product_id == product_id,
            Order.status == "paid"
        )
        .first()
    )

    sold_qty = int(stats.sold_qty or 0)
    revenue = float(stats.revenue or 0)

    return render_template(
        "catalog/product_stats.html",
        product=product,
        sold_qty=sold_qty,
        revenue=revenue,
    )


@catalog_bp.route("/products/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def create_product():
    form = ProductForm()
    load_category_choices(form)

    if form.validate_on_submit():
        existing_product = Product.query.filter_by(
            product_code=form.product_code.data.strip()
        ).first()

        if existing_product:
            flash("Mã sản phẩm đã tồn tại.", "danger")
            return render_template("catalog/product_form.html", form=form, title="Thêm sản phẩm")

        product = Product(
            product_code=form.product_code.data.strip(),
            product_name=form.product_name.data.strip(),
            category_id=form.category_id.data,
            price=form.price.data,
            description=form.description.data.strip() if form.description.data else None,
            image_url=form.image_url.data.strip() if form.image_url.data else None,
            status=form.status.data
        )

        db.session.add(product)
        db.session.commit()

        flash("Thêm sản phẩm thành công.", "success")
        return redirect(url_for("catalog.products_list"))

    return render_template("catalog/product_form.html", form=form, title="Thêm sản phẩm")


@catalog_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    load_category_choices(form)

    if form.validate_on_submit():
        existing_product = Product.query.filter(
            Product.product_code == form.product_code.data.strip(),
            Product.product_id != product.product_id
        ).first()

        if existing_product:
            flash("Mã sản phẩm đã tồn tại ở sản phẩm khác.", "danger")
            return render_template("catalog/product_form.html", form=form, title="Sửa sản phẩm")

        product.product_code = form.product_code.data.strip()
        product.product_name = form.product_name.data.strip()
        product.category_id = form.category_id.data
        product.price = form.price.data
        product.description = form.description.data.strip() if form.description.data else None
        product.image_url = form.image_url.data.strip() if form.image_url.data else None
        product.status = form.status.data

        db.session.commit()

        flash("Cập nhật sản phẩm thành công.", "success")
        return redirect(url_for("catalog.products_list"))

    return render_template("catalog/product_form.html", form=form, title="Sửa sản phẩm")


@catalog_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
@role_required("ADMIN", "MANAGER")
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    used_in_orders = OrderItem.query.filter_by(product_id=product_id).first()
    if used_in_orders:
        flash("Không thể xóa sản phẩm này vì đã phát sinh trong đơn hàng.", "danger")
        return redirect(url_for("catalog.products_list"))

    db.session.delete(product)
    db.session.commit()
    flash("Xóa sản phẩm thành công.", "success")
    return redirect(url_for("catalog.products_list"))
