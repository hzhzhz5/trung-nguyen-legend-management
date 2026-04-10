from flask_wtf import FlaskForm
from wtforms import StringField, TimeField, SelectField, DateField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, Email

class StoreForm(FlaskForm):
    store_code = StringField(
        "Mã cửa hàng",
        validators=[DataRequired(), Length(max=20)]
    )
    store_name = StringField(
        "Tên cửa hàng",
        validators=[DataRequired(), Length(max=100)]
    )
    address = StringField(
        "Địa chỉ",
        validators=[Optional(), Length(max=255)]
    )
    phone = StringField(
        "Số điện thoại",
        validators=[Optional(), Length(max=20)]
    )
    open_time = TimeField(
        "Giờ mở cửa",
        format="%H:%M",
        validators=[Optional()]
    )
    close_time = TimeField(
        "Giờ đóng cửa",
        format="%H:%M",
        validators=[Optional()]
    )
    status = SelectField(
        "Trạng thái",
        choices=[
            ("active", "Hoạt động"),
            ("inactive", "Ngưng hoạt động")
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Lưu")


class EmployeeForm(FlaskForm):
    employee_code = StringField(
        "Mã nhân viên",
        validators=[DataRequired(), Length(max=20)]
    )
    full_name = StringField(
        "Họ và tên",
        validators=[DataRequired(), Length(max=100)]
    )
    gender = SelectField(
        "Giới tính",
        choices=[
            ("Nam", "Nam"),
            ("Nữ", "Nữ"),
            ("Khác", "Khác")
        ],
        validators=[DataRequired()]
    )
    date_of_birth = DateField(
        "Ngày sinh",
        format="%Y-%m-%d",
        validators=[Optional()]
    )
    phone = StringField(
        "Số điện thoại",
        validators=[Optional(), Length(max=20)]
    )
    email = StringField(
        "Email",
        validators=[Optional(), Email(), Length(max=100)]
    )
    address = StringField(
        "Địa chỉ",
        validators=[Optional(), Length(max=255)]
    )
    hire_date = DateField(
        "Ngày vào làm",
        format="%Y-%m-%d",
        validators=[Optional()]
    )
    store_id = SelectField(
        "Cửa hàng",
        coerce=int,
        validators=[DataRequired()]
    )
    status = SelectField(
        "Trạng thái",
        choices=[
            ("active", "Đang làm việc"),
            ("inactive", "Ngưng làm việc")
        ],
        validators=[DataRequired()]
    )

    # Phần tài khoản
    create_account = BooleanField("Tạo tài khoản đăng nhập")
    username = StringField(
        "Tên đăng nhập",
        validators=[Optional(), Length(min=3, max=50)]
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[Optional(), Length(min=6, max=100)]
    )
    role_id = SelectField(
        "Vai trò tài khoản",
        coerce=int,
        choices=[(0, "-- Chọn vai trò --")]
    )

    submit = SubmitField("Lưu")