from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField(
        "Tên đăng nhập",
        validators=[DataRequired(), Length(min=3, max=50)]
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[DataRequired(), Length(min=3, max=100)]
    )
    submit = SubmitField("Đăng nhập")