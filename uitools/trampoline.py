"""Greenlet-based main-thread trampolining for UIs.

During the normal execution of a function, it will be running in the
main thread. However, special functions (provided by this module) will
allow for that function to be interrupted, leave the main thread, wait
for some action, and then resume the function back in the main thread.

@trampoline.decorate(call_in_main_thread)
def test_something(self):

    # We are running in the main thread.
    dialog = my_tool.run()

    # Fall back out of the main event loop while we want for the following
    # to become true.
    button = trampoline.wait_for_qpath(dialog, '//QPushButton[@enabled]', timeout=5)[0]

    # Do something else in the main thread.

    # Wait a second while letting the event loop resume.
    trampoline.sleep(1)


"""

import functools
import time

import greenlet

from qpath import qpath


def decorate(call_in_main_thread):
    def _decorator(func):

        def _construct_and_start(args, kwargs):
            print '_construct_and_start'
            g = greenlet.greenlet(func)
            res = g.switch(*args, **kwargs)
            print '_construct_and_start DONE'
            return g, res

        def _decorated(*args, **kwargs):
            print '_decorated'
            g = None
            res = None
            while g is None or not g.dead:

                print 'loop'

                exc = None
                if res is not None:
                    print 'calling', repr(res)
                    try:
                        res = res()
                    except Exception as exc:
                        pass

                if g is None:
                    g, res = call_in_main_thread(_construct_and_start, args, kwargs)

                else:
                    if exc:
                        call_in_main_thread(g.throw, exc)
                    else:
                        res = call_in_main_thread(g.switch, res)

            return res

        return _decorated
    return _decorator


def wait_for_qpath(root, query, timeout=None):
    pass


def bounce():
    print 'bouncing up...'
    greenlet.getcurrent().parent.switch(None)
    print 'and back down'


def sleep(seconds):
    print 'going to sleep'
    current = greenlet.getcurrent()
    current.parent.switch(functools.partial(time.sleep, seconds))
    print 'returned from sleep'



if __name__ == '__main__':

    import sys

    class Flusher(object):
        def __init__(self, obj):
            self.obj = obj

        def write(self, msg):
            self.obj.write(msg)
            self.obj.flush()

    sys.stdout = Flusher(sys.stdout)


    def main_thread(func, *args, **kwargs):
        print '>>> ENTER MAIN THREAD:', func, args, kwargs
        res = func(*args, **kwargs)
        print '<<< LEAVE MAIN THREAD'
        return res

    @decorate(main_thread)
    def test(*args, **kwargs):
        print 'func started with', args, kwargs
        sleep(0.1)
        bounce()

    print 'Starting...'

    res = test(1, 2, 3, key='value')

    print 'Done.'
    print 'Return value:', repr(res)


