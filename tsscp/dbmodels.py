from werkzeug.security import generate_password_hash as gen_hash, check_password_hash as check_hash
from flask_login import UserMixin, AnonymousUserMixin

from . import consts as c
from . import db
from . import login_manager
from .utils import md2html


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nick = db.Column(db.Unicode(c.NAME_MAX_LENGTH), nullable=False, unique=True)
    member_since = db.Column(db.DateTime, nullable=False)
    last_seen = db.Column(db.DateTime, nullable=False)  # not used now
    password_hash = db.Column(db.String(100), nullable=False)
    banned = db.Column(db.Boolean, nullable=False, default=False)
    op = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)


    def get_id(self):
        return self.uid

    @property
    def password(self):
        raise AttributeError('password is not writable')

    @password.setter
    def password(self, pwd):
        self.password_hash = gen_hash(pwd, 'pbkdf2:sha256', 16)

    def check_password(self, pwd):
        return check_hash(self.password_hash, pwd)

    def __str__(self):
        return '{}\t{}\t{}\t{}\t{}\t{}'.format(self.uid, self.nick, self.member_since, self.last_seen, self.banned, self.op)

    @staticmethod
    def list_title():
        return 'uid\tnick\tmember_since\tlast_seen\tbanned\top'


class Anonymous(AnonymousUserMixin):
    @property
    def uid(self):
        return None

    @property
    def banned(self):
        return True

    @property
    def op(self):
        return False

login_manager.anonymous_user = Anonymous


class Page(db.Model):
    __tablename__ = 'pages'
    pid = db.Column(db.Unicode(c.PID_MAX_LENGTH), nullable=False, primary_key=True)
    removed = db.Column(db.Boolean, nullable=False, default=False)  # not used now

    def __str__(self):
        return '{}\t{}'.format(self.pid, self.removed)

    @staticmethod
    def list_title():
        return 'pid\tremoved'


class Edit(db.Model):
    __tablename__ = 'edits'
    eid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pid = db.Column(db.Unicode(c.PID_MAX_LENGTH), db.ForeignKey('pages.pid'), nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    post_at = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Unicode(c.TITLE_MAX_LENGTH), nullable=False, default='')
    content = db.Column(db.UnicodeText, nullable=False, default='')
    content_parsed = db.Column(db.UnicodeText, nullable=False, default='')

    @staticmethod
    def on_change_content(target, value, oldvalue, initiator):
        target.content_parsed = md2html(value)

    def __str__(self):
        return '{}\t{}\t{}\t{}\t{}\t<{} chars>'.format(self.eid, self.pid, self.uid, self.post_at, self.title, len(self.content))

    @staticmethod
    def list_title():
        return 'eid\tpid\tuid\tpost_at\ttitle\tcontent'

db.event.listen(Edit.content, 'set', Edit.on_change_content)
