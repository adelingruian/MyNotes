from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, EmailField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField

class CreateActivityForm(FlaskForm):
    title = StringField("Activity Title", validators=[DataRequired()])
    description = CKEditorField("Description", validators=[DataRequired()])
    due_date = DateField("Due date", validators=[DataRequired()])
    submit = SubmitField("Submit activity")

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign up")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")
