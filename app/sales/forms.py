from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Length

class CreateOrderForm(FlaskForm):
    table_id = SelectField("Chọn bàn", coerce=int, validators=[DataRequired()])
    note = StringField("Ghi chú", validators=[Optional(), Length(max=255)])
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