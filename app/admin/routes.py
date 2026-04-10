from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from app.admin import admin_bp
from app.admin.forms import StoreForm, EmployeeForm
from app.decorators import role_required
from app.extensions import db
from app.models.store import Store
from app.models.employee import Employee
from app.models.user_account import UserAccount
from app.models.role import Role


def load_store_choices(form):
    stores = Store.query.order_by(Store.store_name.asc()).all()
    form.store_id.choices = [
        (store.store_id, f"{store.store_code} - {store.store_name}")
        for store in stores
    ]

def load_role_choices(form):
    roles = Role.query.filter(Role.role_name.in_(["MANAGER", "STAFF"])).order_by(Role.role_name.asc()).all()
    form.role_id.choices = [(0, "-- Chọn vai trò --")] + [
        (role.role_id, role.role_name) for role in roles
    ]


def get_existing_active_manager(store_id, exclude_employee_id=None):
    query = (
        db.session.query(UserAccount)
        .join(Role, UserAccount.role_id == Role.role_id)
        .join(Employee, UserAccount.employee_id == Employee.employee_id)
        .filter(
            Role.role_name == "MANAGER",
            Employee.store_id == store_id,
            Employee.status == "active",
            UserAccount.status == "active"
        )
    )

    if exclude_employee_id is not None:
        query = query.filter(Employee.employee_id != exclude_employee_id)

    return query.first()


def validate_account_input(form, exclude_account_id=None, exclude_employee_id=None):
    if not form.create_account.data:
        return True, None

    username = (form.username.data or "").strip()
    password = form.password.data or ""

    if not username:
        flash("Bạn đã chọn tạo tài khoản nhưng chưa nhập username.", "danger")
        return False, None

    if form.role_id.data == 0:
        flash("Bạn đã chọn tạo tài khoản nhưng chưa chọn vai trò.", "danger")
        return False, None

    # Khi tạo account mới thì bắt buộc phải có password
    if exclude_account_id is None and not password:
        flash("Bạn phải nhập mật khẩu khi tạo tài khoản mới.", "danger")
        return False, None

    # Kiểm tra trùng username
    username_query = UserAccount.query.filter(UserAccount.username == username)
    if exclude_account_id is not None:
        username_query = username_query.filter(UserAccount.account_id != exclude_account_id)

    if username_query.first():
        flash("Username đã tồn tại. Vui lòng chọn username khác.", "danger")
        return False, None

    role = db.session.get(Role, form.role_id.data)
    if not role:
        flash("Vai trò tài khoản không hợp lệ.", "danger")
        return False, None

    # Rule: mỗi cửa hàng chỉ có 1 manager active
    if role.role_name == "MANAGER":
        existing_manager = get_existing_active_manager(
            store_id=form.store_id.data,
            exclude_employee_id=exclude_employee_id
        )
        if existing_manager:
            flash("Cửa hàng này đã có một quản lý active rồi.", "danger")
            return False, None

    return True, role


# =========================
# STORE ROUTES
# =========================

@admin_bp.route("/stores")
@login_required
@role_required("ADMIN")
def stores_list():
    stores = Store.query.order_by(Store.store_id.desc()).all()
    return render_template("admin/stores_list.html", stores=stores)


@admin_bp.route("/stores/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN")
def create_store():
    form = StoreForm()

    if form.validate_on_submit():
        existing_store = Store.query.filter_by(
            store_code=form.store_code.data.strip()
        ).first()

        if existing_store:
            flash("Mã cửa hàng đã tồn tại.", "danger")
            return render_template("admin/store_form.html", form=form, title="Thêm cửa hàng")

        store = Store(
            store_code=form.store_code.data.strip(),
            store_name=form.store_name.data.strip(),
            address=form.address.data.strip() if form.address.data else None,
            phone=form.phone.data.strip() if form.phone.data else None,
            open_time=form.open_time.data,
            close_time=form.close_time.data,
            status=form.status.data
        )

        db.session.add(store)
        db.session.commit()

        flash("Thêm cửa hàng thành công.", "success")
        return redirect(url_for("admin.stores_list"))

    return render_template("admin/store_form.html", form=form, title="Thêm cửa hàng")


@admin_bp.route("/stores/<int:store_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("ADMIN")
def edit_store(store_id):
    store = Store.query.get_or_404(store_id)
    form = StoreForm(obj=store)

    if form.validate_on_submit():
        existing_store = Store.query.filter(
            Store.store_code == form.store_code.data.strip(),
            Store.store_id != store.store_id
        ).first()

        if existing_store:
            flash("Mã cửa hàng đã tồn tại ở cửa hàng khác.", "danger")
            return render_template("admin/store_form.html", form=form, title="Sửa cửa hàng")

        store.store_code = form.store_code.data.strip()
        store.store_name = form.store_name.data.strip()
        store.address = form.address.data.strip() if form.address.data else None
        store.phone = form.phone.data.strip() if form.phone.data else None
        store.open_time = form.open_time.data
        store.close_time = form.close_time.data
        store.status = form.status.data

        db.session.commit()

        flash("Cập nhật cửa hàng thành công.", "success")
        return redirect(url_for("admin.stores_list"))

    return render_template("admin/store_form.html", form=form, title="Sửa cửa hàng")


@admin_bp.route("/stores/<int:store_id>/delete", methods=["POST"])
@login_required
@role_required("ADMIN")
def delete_store(store_id):
    store = Store.query.get_or_404(store_id)

    if store.employees:
        flash("Không thể xóa cửa hàng đang có nhân viên.", "danger")
        return redirect(url_for("admin.stores_list"))

    db.session.delete(store)
    db.session.commit()

    flash("Xóa cửa hàng thành công.", "success")
    return redirect(url_for("admin.stores_list"))


# =========================
# EMPLOYEE ROUTES
# =========================

@admin_bp.route("/employees")
@login_required
@role_required("ADMIN")
def employees_list():
    employees = Employee.query.order_by(Employee.employee_id.desc()).all()
    return render_template("admin/employees_list.html", employees=employees)


@admin_bp.route("/employees/create", methods=["GET", "POST"])
@login_required
@role_required("ADMIN")
def create_employee():
    form = EmployeeForm()
    load_store_choices(form)
    load_role_choices(form)

    if form.validate_on_submit():
        existing_employee = Employee.query.filter_by(
            employee_code=form.employee_code.data.strip()
        ).first()

        if existing_employee:
            flash("Mã nhân viên đã tồn tại.", "danger")
            return render_template("admin/employee_form.html", form=form, title="Thêm nhân viên")

        is_valid_account, selected_role = validate_account_input(form)
        if not is_valid_account:
            return render_template("admin/employee_form.html", form=form, title="Thêm nhân viên")

        employee = Employee(
            employee_code=form.employee_code.data.strip(),
            full_name=form.full_name.data.strip(),
            gender=form.gender.data,
            date_of_birth=form.date_of_birth.data,
            phone=form.phone.data.strip() if form.phone.data else None,
            email=form.email.data.strip() if form.email.data else None,
            address=form.address.data.strip() if form.address.data else None,
            hire_date=form.hire_date.data,
            store_id=form.store_id.data,
            status=form.status.data
        )

        db.session.add(employee)
        db.session.flush()

        if form.create_account.data:
            account = UserAccount(
                username=form.username.data.strip(),
                role_id=selected_role.role_id,
                employee_id=employee.employee_id,
                status=form.status.data
            )
            account.set_password(form.password.data)
            db.session.add(account)

        db.session.commit()

        flash("Thêm nhân viên thành công.", "success")
        return redirect(url_for("admin.employees_list"))

    return render_template("admin/employee_form.html", form=form, title="Thêm nhân viên")


@admin_bp.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("ADMIN")
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    form = EmployeeForm(obj=employee)

    load_store_choices(form)
    load_role_choices(form)

    # Prefill dữ liệu tài khoản khi GET
    if request.method == "GET" and employee.user_account:
        form.create_account.data = True
        form.username.data = employee.user_account.username
        form.role_id.data = employee.user_account.role_id

    if form.validate_on_submit():
        existing_employee = Employee.query.filter(
            Employee.employee_code == form.employee_code.data.strip(),
            Employee.employee_id != employee.employee_id
        ).first()

        if existing_employee:
            flash("Mã nhân viên đã tồn tại ở nhân viên khác.", "danger")
            return render_template("admin/employee_form.html", form=form, title="Sửa nhân viên")

        current_account_id = employee.user_account.account_id if employee.user_account else None

        is_valid_account, selected_role = validate_account_input(
            form,
            exclude_account_id=current_account_id,
            exclude_employee_id=employee.employee_id
        )
        if not is_valid_account:
            return render_template("admin/employee_form.html", form=form, title="Sửa nhân viên")

        employee.employee_code = form.employee_code.data.strip()
        employee.full_name = form.full_name.data.strip()
        employee.gender = form.gender.data
        employee.date_of_birth = form.date_of_birth.data
        employee.phone = form.phone.data.strip() if form.phone.data else None
        employee.email = form.email.data.strip() if form.email.data else None
        employee.address = form.address.data.strip() if form.address.data else None
        employee.hire_date = form.hire_date.data
        employee.store_id = form.store_id.data
        employee.status = form.status.data

        if form.create_account.data:
            if employee.user_account:
                employee.user_account.username = form.username.data.strip()
                employee.user_account.role_id = selected_role.role_id
                employee.user_account.status = form.status.data

                if form.password.data:
                    employee.user_account.set_password(form.password.data)
            else:
                new_account = UserAccount(
                    username=form.username.data.strip(),
                    role_id=selected_role.role_id,
                    employee_id=employee.employee_id,
                    status=form.status.data
                )
                new_account.set_password(form.password.data)
                db.session.add(new_account)
        else:
            # Nếu bỏ tick tạo tài khoản mà nhân viên đang có account,
            # ta không xóa mà chỉ khóa account lại
            if employee.user_account:
                employee.user_account.status = "inactive"

        db.session.commit()

        flash("Cập nhật nhân viên thành công.", "success")
        return redirect(url_for("admin.employees_list"))

    return render_template("admin/employee_form.html", form=form, title="Sửa nhân viên")


@admin_bp.route("/employees/<int:employee_id>/delete", methods=["POST"])
@login_required
@role_required("ADMIN")
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    if employee.user_account:
        flash("Không thể xóa nhân viên đã có tài khoản đăng nhập.", "danger")
        return redirect(url_for("admin.employees_list"))

    db.session.delete(employee)
    db.session.commit()

    flash("Xóa nhân viên thành công.", "success")
    return redirect(url_for("admin.employees_list"))