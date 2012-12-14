"""Functions for working with threads in Qt applications. Usually for dealing
with running in the main event loop (e.g. thread) or not.

We want to be able to use these functions and have them present reasonable
actions even if there is no event loop. In most cases, that means immediately
calling the function.

"""

import thread
import Queue as queue
import traceback

from .qt import QtCore, QtGui



# We can only really tell when the event loop as started, not when it has shut
# down.
_is_running = False


if QtCore:

    def _process_call_in_main_thread(res_queue, func, args, kwargs):

        try:
            res = func(*args, **kwargs)

        except Exception as e:

            if res_queue:
                res_queue.put((False, e))
            else:
                sys.stderr.write('Uncaught exception in main thread.\n')
                traceback.print_exc()

        else:
            if res_queue:
                res_queue.put((True, res))


    class _MainThreadDispatcher(QtCore.QObject):

        # Signature: return_queue (may be None), callable, args, kwargs
        call = QtCore.pyqtSignal([object, object, object, object])

        def __init__(self):
            super(_MainThreadDispatcher, self).__init__()
            self.call.connect(_process_call_in_main_thread)


    _main_thread_dispatcher = _MainThreadDispatcher()


    # This will run in the first cycle through the event loop, before
    # any of the following functions have had a chance to be called
    # after the event loop starts. If this is called in the main event
    # loop it will be processed immediately.
    def _signal_when_running():
        global _is_running
        _is_running = True
    _main_thread_dispatcher.call.emit(None, _signal_when_running, (), {})



def defer_to_main_thread(func, *args, **kwargs):
    """Call the given function in the main thread, but don't wait for results.

    If an exception is thrown, a traceback will be printed.

    If Qt is not running, it will call the function immediately.

    """

    if not _is_running:
        func(*args, **kwargs)
        return

    # Don't need to bother doing anything fancy since the signal will deal with
    # making sure that it runs on the main loop.
    _main_thread_dispatcher.call.emit(None, func, args, kwargs)


def main_thread_ident():
    """Get the :func:`python:thread.get_ident` for the main_thread.

    If Qt is not running, returns ``None``.

    """
    if main_thread_ident._value is None:
        if not _is_running:
            return None
        main_thread_ident._value = call_in_main_thread(thread.get_ident)
    return main_thread_ident._value

main_thread_ident._value = None


def is_main_thread():
    """Return True if this is in the main thread (or Qt is not running)."""
    if not _is_running:
        return True
    return main_thread_ident() == thread.get_ident()


def call_in_main_thread(func, *args, **kwargs):
    """Call the given function in the main thread, and wait for results.

    If an exception is thrown, it will be reraised here.

    If Qt is not running, it will call the function immediately.

    """
    
    if not _is_running:
        return func(*args, **kwargs)

    res_queue = queue.Queue()
    _main_thread_dispatcher.call.emit(res_queue, func, args, kwargs)
    ok, res = res_queue.get()
    if ok:
        return res
    else:
        raise res




