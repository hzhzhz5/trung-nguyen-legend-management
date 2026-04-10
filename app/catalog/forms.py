from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class TableForm(FlaskForm):
    store_id = SelectField("Cửa hàng", coerce=int, validators=[DataRequired()])
    table_code = StringField("Mã bàn", validators=[DataRequired(), Length(max=20)])
    capacity = IntegerField("Sức chứa", validators=[DataRequired(), NumberRange(min=1, max=20)])
    status = SelectField(
        "Trạng thái",
        choices=[
            ("empty", "Trống"),
            ("occupied", "Đang phục vụ"),
            ("unavailable", "Khóa")
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Lưu")


class CategoryForm(FlaskForm):
    category_name = StringField("Tên danh mục", validators=[DataRequired(), Length(max=100)])
    description = StringField("Mô tả", validators=[Optional(), Length(max=255)])
    status = SelectField(
        "Trạng thái",
        choices=[
            ("active", "Hoạt động"),
            ("inactive", "Ngưng hoạt động")
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Lưu")


class ProductForm(FlaskForm):
    product_code = StringField("Mã sản phẩm", validators=[DataRequired(), Length(max=20)])
    product_name = StringField("Tên sản phẩm", validators=[DataRequired(), Length(max=100)])
    category_id = SelectField("Danh mục", coerce=int, validators=[DataRequired()])
    price = DecimalField("Giá bán", places=2, validators=[DataRequired(), NumberRange(min=0)])
    description = StringField("Mô tả", validators=[Optional(), Length(max=255)])
    image_url = StringField("Ảnh URL", validators=[Optional(), Length(max=255)])
    status = SelectField(
        "Trạng thái",
        choices=[
            ("available", "Đang bán"),
            ("unavailable", "Ngưng bán")
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Lưu")