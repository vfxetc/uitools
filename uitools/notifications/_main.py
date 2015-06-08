import os
import sys


from .core import *

from metatools.apps.runtime import initialize, poll_event_loop, run_event_loop


def main_bundle():

    logfile = open('/tmp/%s.log' % __name__, 'a')
    logfile.write('==========\n')

    class Tee(object):

        def __init__(self, fhs):
            self.fhs = fhs

        def write(self, data):
            for fh in self.fhs:
                fh.write(data)
                fh.flush()

    sys.stdout = Tee((logfile, sys.stdout))
    sys.stderr = Tee((logfile, sys.stderr))

    main()


# Target of the notification app.
def noop():
    pass


def main():

    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument('--loop', action='store_true')
    parser.add_argument('--qt', action='store_true')
    args = parser.parse_args()

    if IS_MACOS:
        initialize(standalone=not (args.loop or args.qt))

    if args.qt:

        from ..qt import Q

        qt_app = Q.Application([])

        button = Q.PushButton("HERE")
        @button.clicked.connect
        def on_button_clicked():
            Notification('Qt', 'You pressed the button in QT').send()
        button.show()

        qt_timer = Q.Timer()
        qt_timer.setInterval(0)

    # Need to keep this around (for the libnotify handle).
    note = Notification('Test', 'This is a test.', subtitle='Subtitle')
    print note
    note.send()


    if args.loop:

        # if IS_LINUX:
        #     glib_loop = QLib.MainLoop()
        #     if args.qt:
        #         def poll_event_loop():
        #             # This must be added every time.
        #             GLib.idle_add(glib_loop.quit)
        #             glib_loop.run()
        #     else:
        #         glib_loop.run()

        if args.qt:
            # Connect the OS loop to the Qt loop, and start it up.
            qt_timer.timeout.connect(poll_event_loop)
            qt_app.exec_()

        else:
            run_event_loop()


if __name__ == '__main__':

    main()