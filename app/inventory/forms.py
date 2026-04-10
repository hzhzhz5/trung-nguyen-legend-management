from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email, NumberRange

class IngredientForm(FlaskForm):
    ingredient_code = StringField("Mã nguyên liệu", validators=[DataRequired(), Length(max=20)])
    ingredient_name = StringField("Tên nguyên liệu", validators=[DataRequired(), Length(max=100)])
    unit = StringField("Đơn vị tính", validators=[DataRequired(), Length(max=20)])
    min_stock_level = DecimalField("Mức tồn tối thiểu", places=2, validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField(
        "Trạng thái",
        choices=[
            ("active", "Hoạt động"),
            ("inactive", "Ngưng hoạt động")
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Lưu")


class SupplierForm(FlaskForm):
    supplier_code = StringField("Mã NCC", validators=[DataRequired(), Length(max=20)])
    supplier_name = StringField("Tên nhà cung cấp", validators=[DataRequired(), Length(max=100)])
    phone = StringField("Số điện thoại", validators=[Optional(), Length(max=20)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=100)])
    address = StringField("Địa chỉ", validators=[Optional(), Length(max=255)])
    status = SelectField(
        "Trạng thái",
        choices=[
            ("active", "Hoạt động"),
            ("inactive", "Ngưng hoạt động")
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Lưu")


class CreatePurchaseOrderForm(FlaskForm):
    supplier_id = SelectField("Nhà cung cấp", coerce=int, validators=[DataRequired()])
    store_id = SelectField("Cửa hàng", coerce=int, validators=[DataRequired()])
    note = StringField("Ghi chú", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Tạo phiếu nhập")


class AddPurchaseOrderItemForm(FlaskForm):
    ingredient_id = SelectField("Nguyên liệu", coerce=int, validators=[DataRequired()])
    quantity = DecimalField("Số lượng", places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    unit_price = DecimalField("Đơn giá", places=2, validators=[DataRequired(), NumberRange(min=0)])
    note = StringField("Ghi chú", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Thêm nguyên liệu")


class ConfirmReceiveForm(FlaskForm):
    submit = SubmitField("Xác nhận nhập kho")