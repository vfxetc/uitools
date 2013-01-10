"""Functions for working with threads in Qt applications. Usually for dealing
with running in the main event loop (e.g. thread) or not.

These functions are known to work as reasonable replacements for the functions
provided by both Maya and Nuke.

We want to be able to use these functions and have them present reasonable
actions even if there is no event loop. In most cases, that means immediately
calling the function.

Another large benefit of these functions is that they are re-rentrant, unlike
the functions provided in either Maya or Nuke which will lock up the main
thread if called from the main thread.

.. warning:: Maya does occasionally output "QMainWindowLayout::count: ?" when
    using these functions, and I haven't determined why.

"""

from __future__ import absolute_import

import Queue as queue
import traceback
import sys

from .qt import QtCore, QtGui


if QtCore:


    class _Event(QtCore.QEvent):

        _type = QtCore.QEvent.registerEventType()

        def __init__(self, res_queue, func, args, kwargs):
            super(_Event, self).__init__(self._type)
            self.res_queue = res_queue
            self.func = func
            self.args = args
            self.kwargs = kwargs

        def process(self):

            self.accept()

            try:
                res = self.func(*self.args, **self.kwargs)

            # Catch EVERYTHING, including KeyboardInterrupt and SystemExit.
            except:

                if self.res_queue:
                    self.res_queue.put((False, sys.exc_info()[1]))
                else:
                    sys.stderr.write('Uncaught exception in main thread.\n')
                    traceback.print_exc()

            else:
                if self.res_queue:
                    self.res_queue.put((True, res))

            return True


    class _Dispatcher(QtCore.QObject):

        def __init__(self):
            super(_Dispatcher, self).__init__()

            self.running = False
            self._app = None

            # If we can grab the app, push over to its thread, and then
            # queue up (or immediately call) the signal.
            if self.app:
                self.moveToThread(self.app.thread())
                self.defer(self.signal_start)

            # Otherwise, schedule a timer to run (assumed to be in the
            # main thread) so that we can grab the app at that point.
            else:
                QtCore.QTimer.singleShot(0, self.signal_start)

        def signal_start(self):
            self.running = True
            if self.thread() is not self.app.thread():
                self.moveToThread(self.app.thread())

        @property
        def app(self):
            if self._app is None:
                self._app = QtGui.QApplication.instance()
            return self._app

        def event(self, event):
            if isinstance(event, _Event):
                return event.process()
            else:
                return super(_Dispatcher, self).event(event)

        def is_main_thread(self):
            return (not self.running) or self.app.thread() is QtCore.QThread.currentThread()

        def defer(self, func, *args, **kwargs):

            if self.is_main_thread():
                func(*args, **kwargs)
                return

            self.app.postEvent(self, _Event(None, func, args, kwargs))

        def call(self, func, *args, **kwargs):

            if self.is_main_thread():
                return func(*args, **kwargs)

            # TODO: Be able to figure out when the function is called
            # but does not throw something into the queue (for whatever
            # reasons, so that we can stop blocking. Perhaps a pair of
            # weakrefs?

            res_queue = queue.Queue()
            self.app.postEvent(self, _Event(res_queue, func, args, kwargs))
            ok, res = res_queue.get()

            if ok:
                return res
            else:
                raise res


    _dispatcher = _Dispatcher()

else:

    _dispatcher = None


def defer_to_main_thread(func, *args, **kwargs):
    """Call the given function in the main thread, but don't wait for results.

    If an exception is thrown, a traceback will be printed.

    This function is re-entrant, and calling from the main thread will call the
    passed function immediately (discarding the result).

    If Qt is not running, it will call the function immediately.

    """
    if not _dispatcher:
        func(*args, **kwargs)
        return
    _dispatcher.defer(func, *args, **kwargs)


def call_in_main_thread(func, *args, **kwargs):
    """Call the given function in the main thread, and wait for results.

    If an exception is thrown, it will be reraised here.

    This function is re-entrant, and calling from the main thread will call the
    passed function immediately.

    If Qt is not running, it will call the function immediately.

    """
    if not _dispatcher:
        return func(*args, **kwargs)
    return _dispatcher.call(func, *args, **kwargs)


def is_main_thread():
    """Return True if this is in the main thread (or Qt is not running)."""
    if not _dispatcher:
        return True
    else:
        return _dispatcher.is_main_thread()






