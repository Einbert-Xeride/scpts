import os

from flask import Flask, render_template, flash, redirect, url_for, abort
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy

from getpass import getpass


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data.db')
    SQLALCHEMY_ECHO = (os.environ.get('FLASK_DEBUG') == 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')


app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager(app)
db = SQLAlchemy(app)
moment = Moment(app)
pagedown = PageDown(app)
bootstrap = Bootstrap(app)


app.add_template_global('SCPTS', 'DOCPREFIX')


login_manager.session_protection = 'strong'
login_manager.login_view = 'login'


from . import models as m
from . import forms as f
from . import utils as u
from . import consts as c


@app.route('/')
def main():
    pages = m.list_page()
    pages_count = m.count_pages()
    users_count = m.count_users()
    return render_template('main.html', pages=pages, pages_count=pages_count, users_count=users_count)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = f.LoginForm()
    if form.validate_on_submit():
        try:
            m.login_user(form.nick.data, form.password.data, form.keep_login.data)
            return redirect(url_for('main'))
        except RuntimeError as e:
            flash(e.args[0])
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    m.logout_user()
    flash('已注销')
    return redirect(url_for('main'))


@app.route('/regist', methods=['GET', 'POST'])
def regist():
    if not current_user.op:
        abort(403)
    form = f.RegistForm()
    if form.validate_on_submit():
        try:
            m.regist_user(form.nick.data, form.password.data)
        except RuntimeError as e:
            flash(e.args[0])
    return render_template("regist.html", form=form)


@app.route('/user/<int:uid>', methods=['GET', 'POST'])
def user(uid):
    user = m.get_user_or_404(uid)
    form_nick = f.ChangeNickForm()
    form_pwd = f.ChangePasswordForm()
    if form_nick.validate_on_submit():
        m.change_nick(form_nick.nick.data)
        flash('修改昵称成功')
    if form_pwd.validate_on_submit():
        try:
            m.change_password(form_pwd.old_password.data, form_pwd.password.data)
            flash('修改密码成功')
        except RuntimeError as e:
            flash(e.args[0])
    return render_template("user.html", user=user, form_nick=form_nick, form_pwd=form_pwd)


@app.route('/page/<string:pid>')
def page(pid):
    u.check_pid_or_404(pid)
    page = m.get_page(pid)
    return render_template('page.html', page=page, pid=pid)


@app.route('/page/<string:pid>/edit', methods=['GET', 'POST'])
def page_edit(pid):
    u.check_pid_or_404(pid)
    form = f.EditPageForm()
    if form.validate_on_submit():
        m.edit_page(pid, form.title.data, form.content.data)
        return redirect(url_for('page', pid=pid))
    form.title.data, form.content.data = m.get_page_title_content_or_empty(pid)
    return render_template('page_edit.html', form=form, pid=pid)


@app.route('/page/<string:pid>/list-edit')
def page_list_edit(pid):
    u.check_pid_or_404(pid)
    edits = m.list_edit(pid)
    return render_template('page_list_edit.html', edits=edits, pid=pid)


@app.route('/edit/<int:eid>')
def edit(eid):
    edit = m.get_edit(eid)
    return render_template('edit.html', edit=edit)


@app.cli.command(name='regist')
def command_regist():
    'Instantly add a new user.'
    nick = input('Nick: ')
    pass1 = getpass()
    pass2 = getpass('Retype: ')
    if pass1 != pass2:
        print('Password mismatch')
    elif len(pass1) < c.PASSWORD_MIN_LENGTH:
        print('Password too short')
    else:
        m._regist_user(nick, pass1)


@app.cli.command(name='deploy')
def command_deploy():
    'Deploy application.'
    from flask_migrate import upgrade
    upgrade()


def _set_op(op):
    nick = input('Nick: ')
    user = m.get_user_by_nick(nick)
    if user is not None:
        m.set_op(user, op)
    else:
        print('User not found')


@app.cli.command(name='op')
def command_op():
    'Make a user op.'
    _set_op(True)


@app.cli.command(name='deop')
def command_deop():
    'Revoke op permission.'
    _set_op(False)


@app.cli.command(name='list-user')
def command_list_user():
    from .dbmodels import User
    print(User.list_title())
    for i in m.list_raw_user():
        print(i)


@app.cli.command(name='list-page')
def command_list_page():
    from .dbmodels import Page
    print(Page.list_title())
    for i in m.list_raw_page():
        print(i)


@app.cli.command(name='list-edit')
def command_list_edit():
    from .dbmodels import Edit
    print(Edit.list_title())
    for i in m.list_raw_edit():
        print(i)


if __name__ == '__main__':
    app.run()
