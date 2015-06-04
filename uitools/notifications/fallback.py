import tempfile
from subprocess import check_call

from .core import IS_LINUX, IS_MACOS, NotifierFailed


class Notification(object):

    def __init__(self, title, message, subtitle=None, sticky=False):

        self.title = title
        self.subtitle = subtitle
        self.message = message
        self.sticky = sticky

        self._sent = False
        self._tempfile = None

    def get_tempfile_path(self):
        if not self._tempfile:
            fd, self._tempfile = tempfile.mkstemp('.txt', 'uitools.notifications.' + re.sub(r'\W+', '-', self.title) + '.')
            os.write(fd, self.message)
            os.close(fd)
        return self._tempfile

    def send_via_fallback(self):

        if IS_LINUX:
            argv = ['notify-send']
            if self.sticky:
                argv.extend(['-t', '3600000'])
            argv.extend([self.title, self.message])
            try:
                check_call(argv)
            except Exception as e:
                pass

        if IS_MACOS:
            argv = ['terminal-notifier',
                '-title', title,
                '-message', message,
                '-open', 'file://' + self.get_tempfile_path(),
            ]
            try:
                return check_call(argv)
            except Exception as e:
                pass

            # AppleScript works since 10.9.
            argv = ['osascript', '-e', 'display notification "%s" with title "%s"' % (
                message.replace('"', '\\"'),
                title.replace('"', '\\"'),
            )]
            try:
                return check_call(argv)
            except Exception as e:
                pass
        
            argv = ['growlnotify',
                '--name', 'Shotgun Action Dispatcher',
                '--title', title,
                '--message', message
            ]
            if self.sticky:
                argv.append('-s')
            try:
                return check_call(argv)
            except Exception as e:
                raise NotifierFailed('all fallbacks failed failed: %s %s' % (e.__type_, e))
