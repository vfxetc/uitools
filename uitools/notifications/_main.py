import os
import sys


from .core import *


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



def main():

    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument('--loop', action='store_true')
    parser.add_argument('--qt', action='store_true')
    args = parser.parse_args()


    if IS_MACOS:
        from .darwin import _setup
        _setup()


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
    note.send()


    if IS_MACOS and not (args.loop or args.qt):
        from .darwin import _catch_startup_events
        _catch_startup_events()
        exit()


    if args.loop:

        if IS_MACOS:
            run_loop = NS.RunLoop.currentRunLoop()
            def run_loop_once(timeout=0):
                # We can either give an instanteous beforeDate and sleep ourselves,
                # or we can give it a positive time.
                until = NS.Date.dateWithTimeIntervalSinceNow_(timeout) # time from now in seconds
                run_loop.runMode_beforeDate_(NS.DefaultRunLoopMode, until)

        if IS_LINUX:
            glib_loop = QLib.MainLoop()
            if args.qt:
                def run_loop_once():
                    # This must be added every time.
                    GLib.idle_add(glib_loop.quit)
                    glib_loop.run()
            else:
                glib_loop.run()

        if args.qt:
            # Connect the OS loop to the Qt loop, and start it up.
            qt_timer.timeout.connect(run_loop_once)
            qt_app.exec_()

        else:

            # If you need applicationDidFinishLaunching, then you must run
            # the real loop (or, perhaps, the fake one above, followed by
            # the real loop).
            ns_app.run()

            # Here is our manual loop.
            while True:
                print 'run_loop_once'
                run_loop_once(1)


if __name__ == '__main__':

    main()