from datetime import datetime
from collections import namedtuple

from werkzeug.exceptions import Forbidden
from flask_login import current_user, login_user as flask_login_user, logout_user

from . import db, login_manager
from .dbmodels import User, Page, Edit


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


def regist_user(nick, password):
    if not current_user.op:
        raise Forbidden
    return _regist_user(nick, password)


def _regist_user(nick, password):
    now = datetime.utcnow()
    user = User(nick=nick, member_since=now, last_seen=now)
    user.password = password
    db.session.add(user)
    db.session.commit()


def login_user(nick, password, keep_login):
    user = User.query.filter_by(nick=nick).first()
    if user is None or not user.check_password(password):
        raise RuntimeError('昵称或密码错误')
    flask_login_user(user, keep_login)


logout_user = logout_user  # make ide happy


def get_user_or_404(uid):
    return User.query.get_or_404(uid)


def get_user_by_nick(nick):
    return User.query.filter_by(nick=nick).first()


def set_op(user, op):
    user.op = op
    db.session.commit()


def change_password(old, new):
    assert current_user.is_authenticated
    if not current_user.check_password(old):
        raise RuntimeError('旧密码错误')
    current_user.password = new
    db.session.commit()


def change_nick(nick):
    assert current_user.is_authenticated
    current_user.nick = nick
    db.session.commit()


def list_raw_user():
    return User.query.order_by(User.uid).all()


def edit_page(pid, title, content):
    assert current_user.is_authenticated
    if current_user.banned:
        raise Forbidden
    now = datetime.utcnow()
    page = Page.query.get(pid)
    if page is None:
        page = Page(pid=pid)
        db.session.add(page)
    edit = Edit(pid=page.pid, uid=current_user.uid, post_at=now, title=title, content=content)
    db.session.add(edit)
    db.session.commit()


def list_page():
    edit_alias = db.aliased(Edit)
    pages = db.session.query(Page.pid, Edit.title)\
        .join(Edit)\
        .order_by(Page.pid)\
        .filter(db.not_(db.session.query(edit_alias.post_at).filter(edit_alias.pid == Page.pid, edit_alias.post_at > Edit.post_at).exists()))\
        .all()
    return [PageListItem(*page) for page in pages]

PageListItem = namedtuple('PageListItem', ('pid', 'title'))


def list_raw_page():
    return Page.query.order_by(Page.pid).all()


def get_page(pid):
    return Edit.query.filter_by(pid=pid).order_by(db.desc(Edit.post_at)).first_or_404()


def get_page_title_content_or_empty(pid):
    edit = Edit.query.filter_by(pid=pid).order_by(db.desc(Edit.post_at)).first()
    if edit is not None:
        return edit.title, edit.content
    else:
        return '', ''


def list_edit(pid):
    edits = db.session.query(Edit.eid, Edit.post_at, Edit.title, User.uid, User.nick)\
        .join(User)\
        .filter(Edit.pid == pid)\
        .order_by(db.desc(Edit.post_at))\
        .all()
    return [EditListItem(*edit) for edit in edits]

EditListItem = namedtuple('EditListItem', ('eid', 'post_at', 'title', 'uid', 'nick'))


def get_edit(eid):
    return Edit.query.get_or_404(eid)


def list_raw_edit():
    return Edit.query.order_by(Edit.eid).all()


def count_users():
    return db.session.query(db.func.count(User.uid)).first()[0]


def count_pages():
    return db.session.query(db.func.count(Page.pid)).first()[0]


def count_edits(pid):
    return db.session.query(db.func.count(Edit.eid)).filter(Edit.pid == pid).first()[0]
