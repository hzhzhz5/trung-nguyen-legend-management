from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Length


class CreateOrderForm(FlaskForm):
    order_type = SelectField(
        "Loại đơn",
        choices=[
            ("dine_in", "Khách ngồi tại quán"),
            ("takeaway", "Khách mua mang về"),
            ("delivery", "Ship nước"),
        ],
        validators=[DataRequired()]
    )

    table_id = SelectField("Chọn bàn", coerce=int, validators=[Optional()])

    customer_name = StringField("Tên khách", validators=[Optional(), Length(max=100)])
    customer_phone = StringField("SĐT", validators=[Optional(), Length(max=20)])
    delivery_address = StringField("Địa chỉ", validators=[Optional(), Length(max=255)])

    note = StringField("Ghi chú đơn", validators=[Optional(), Length(max=255)])

    product_id = SelectField("Món đầu tiên", coerce=int, validators=[DataRequired()])
    quantity = IntegerField("Số lượng", validators=[DataRequired(), NumberRange(min=1, max=100)])
    item_note = StringField("Ghi chú món", validators=[Optional(), Length(max=255)])

    submit = SubmitField("Tạo đơn hàng")


class AddOrderItemForm(FlaskForm):
    product_id = SelectField("Sản phẩm", coerce=int, validators=[DataRequired()])
    quantity = IntegerField("Số lượng", validators=[DataRequired(), NumberRange(min=1, max=100)])
    note = StringField("Ghi chú món", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Thêm món")


class PaymentForm(FlaskForm):
    payment_method = SelectField(
        "Phương thức thanh toán",
        choices=[
            ("cash", "Tiền mặt"),
            ("card", "Thẻ"),
            ("transfer", "Chuyển khoản")
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField("Xác nhận thanh toán")