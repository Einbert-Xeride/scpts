from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired as Required, Length, EqualTo, Regexp
from flask_pagedown.fields import PageDownField
from . import consts as c


class LoginForm(Form):
    nick = StringField('昵称', validators=[
        Required(),
        Length(c.NAME_MIN_LENGTH, c.NAME_MAX_LENGTH)
    ])
    password = PasswordField('密码', validators=[
        Required(),
        Length(c.PASSWORD_MIN_LENGTH)
    ])
    keep_login = BooleanField('保持登录')
    submit = SubmitField('登录')


class RegistForm(Form):
    nick = StringField('昵称', validators=[
        Required(),
        Length(c.NAME_MIN_LENGTH, c.NAME_MAX_LENGTH),
        Regexp('^\w+$', 0, '昵称只能包含文字、数字、下划线')
    ])
    password = PasswordField('密码', validators=[
        Required(),
        Length(c.PASSWORD_MIN_LENGTH),
        EqualTo('password2')
    ])
    password2 = PasswordField('确认密码', validators=[
        Required(),
        Length(c.PASSWORD_MIN_LENGTH)
    ])
    submit = SubmitField('注册')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[
        Required(),
        Length(c.PASSWORD_MIN_LENGTH)
    ])
    password = PasswordField('新密码', validators=[
        Required(),
        Length(c.PASSWORD_MIN_LENGTH),
        EqualTo('password2')
    ])
    password2 = PasswordField('确认密码', validators=[
        Required(),
        Length(c.PASSWORD_MIN_LENGTH)
    ])
    submit = SubmitField('修改密码')


class ChangeNickForm(Form):
    nick = StringField('昵称', validators=[
        Required(),
        Length(c.NAME_MIN_LENGTH, c.NAME_MAX_LENGTH),
        Regexp('^\w+$', 0, '昵称只能包含文字、数字、下划线')
    ])
    submit = SubmitField('修改昵称')


class EditPageForm(Form):
    title = StringField('标题', validators=[
        Required(),
        Length(max=c.TITLE_MAX_LENGTH)
    ])
    content = PageDownField('正文', validators=[
        Required()
    ])
    submit = SubmitField('提交')
