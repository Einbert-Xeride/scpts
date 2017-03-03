from markdown import markdown
import bleach
import re
from werkzeug.exceptions import NotFound
from . import consts as c


def md2html(md: str):
    allowed_tags = ('a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'table', 'tr', 'td', 'thead', 'tbody', 'th', 'sub', 'sup',
                    'del')
    return bleach.linkify(bleach.clean(markdown(md, output_format='html'), tags=allowed_tags, strip=True))


def check_pid(pid):
    return _pid_check_re.match(pid) is not None and len(pid) < c.PID_MAX_LENGTH

_pid_check_re = re.compile('^[A-Za-z0-9_]+$')


def check_pid_or_404(pid):
    if not check_pid(pid):
        raise NotFound
