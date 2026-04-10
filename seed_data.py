from datetime import date, time

from app import create_app
from app.extensions import db
from app.models.role import Role
from app.models.store import Store
from app.models.employee import Employee
from app.models.user_account import UserAccount

app = create_app()

with app.app_context():
    # 1. Tạo role
    roles_data = [
        {"role_name": "ADMIN", "description": "Quản trị toàn hệ thống"},
        {"role_name": "MANAGER", "description": "Quản lý cửa hàng"},
        {"role_name": "STAFF", "description": "Nhân viên"}
    ]

    for item in roles_data:
        role = Role.query.filter_by(role_name=item["role_name"]).first()
        if not role:
            role = Role(
                role_name=item["role_name"],
                description=item["description"]
            )
            db.session.add(role)

    db.session.commit()

    # 2. Tạo store mẫu
    store = Store.query.filter_by(store_code="CH001").first()
    if not store:
        store = Store(
            store_code="CH001",
            store_name="Trung Nguyên Legend Cầu Giấy",
            address="123 Cầu Giấy, Hà Nội",
            phone="0900000000",
            open_time=time(7, 0),
            close_time=time(22, 0),
            status="active"
        )
        db.session.add(store)
        db.session.commit()

    # 3. Tạo employee mẫu
    manager_emp = Employee.query.filter_by(employee_code="NVQL001").first()
    if not manager_emp:
        manager_emp = Employee(
            employee_code="NVQL001",
            full_name="Nguyễn Văn Quản Lý",
            gender="Nam",
            date_of_birth=date(1995, 5, 10),
            phone="0900000001",
            email="manager@example.com",
            address="Hà Nội",
            hire_date=date(2024, 1, 10),
            store_id=store.store_id,
            status="active"
        )
        db.session.add(manager_emp)

    staff_emp = Employee.query.filter_by(employee_code="NV001").first()
    if not staff_emp:
        staff_emp = Employee(
            employee_code="NV001",
            full_name="Trần Thị Nhân Viên",
            gender="Nữ",
            date_of_birth=date(2000, 8, 20),
            phone="0900000002",
            email="staff@example.com",
            address="Hà Nội",
            hire_date=date(2024, 2, 1),
            store_id=store.store_id,
            status="active"
        )
        db.session.add(staff_emp)

    db.session.commit()

    # 4. Lấy lại role và employee sau commit
    admin_role = Role.query.filter_by(role_name="ADMIN").first()
    manager_role = Role.query.filter_by(role_name="MANAGER").first()
    staff_role = Role.query.filter_by(role_name="STAFF").first()

    manager_emp = Employee.query.filter_by(employee_code="NVQL001").first()
    staff_emp = Employee.query.filter_by(employee_code="NV001").first()

    # 5. Tạo tài khoản admin
    admin_user = UserAccount.query.filter_by(username="admin").first()
    if not admin_user:
        admin_user = UserAccount(
            username="admin",
            role_id=admin_role.role_id,
            employee_id=None,
            status="active"
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)

    # 6. Tạo tài khoản manager
    manager_user = UserAccount.query.filter_by(username="manager").first()
    if not manager_user:
        manager_user = UserAccount(
            username="manager",
            role_id=manager_role.role_id,
            employee_id=manager_emp.employee_id,
            status="active"
        )
        manager_user.set_password("manager123")
        db.session.add(manager_user)

    # 7. Tạo tài khoản staff
    staff_user = UserAccount.query.filter_by(username="staff").first()
    if not staff_user:
        staff_user = UserAccount(
            username="staff",
            role_id=staff_role.role_id,
            employee_id=staff_emp.employee_id,
            status="active"
        )
        staff_user.set_password("staff123")
        db.session.add(staff_user)

    db.session.commit()

    print("Seed dữ liệu thành công.")
    print("=== TÀI KHOẢN MẪU ===")
    print("ADMIN   -> admin / admin123")
    print("MANAGER -> manager / manager123")
    print("STAFF   -> staff / staff123")