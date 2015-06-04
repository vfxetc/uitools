#!/usr/bin/python

import json
import os
import site
import sys
import traceback


IS_MACOS = sys.platform == 'darwin'
IS_LINUX  = sys.platform.startswith('linux')


if IS_MACOS:

    extras = '/System/Library/Frameworks/Python.framework/Versions/Current/Extras/lib/python'
    site.addsitedir(extras)
    try:
        from PyObjCTools import AppHelper
        import AppKit
        import CoreFoundation
        import Foundation
        import objc
    except ImportError:
        objc = NS = CF = None

    else:

        class ModuleProxy(object):

            def __init__(self, prefixes, modules):
                self.prefixes = prefixes
                self.modules = modules

            def __getattr__(self, name):
                for prefix in self.prefixes:
                    fullname = prefix + name
                    for module in self.modules:
                        obj = getattr(module, fullname, None)
                        if obj is not None:
                            setattr(self, name, obj)
                            return obj
                raise AttributeError(name)

        NS = ModuleProxy(['NS'], [Foundation, AppKit])
        CF = ModuleProxy(['CF'], [CoreFoundation])

        class _Delegate(NS.Object):

            _instance = None

            @classmethod
            def instance(cls):
                obj = cls._instance
                if not obj:
                    obj = cls._instance = cls.alloc().init()
                return obj
            
            def __init__(self):
                super(_Delegate, self).__init__()
                self._next_delegate = None

            def applicationWillFinishLaunching_(self, notification):
                print "applicationWillFinishLaunching:%s" % notification
                delegate = NS.App.delegate()
                if delegate is not self:
                    # Seems like Qt has replaced us as the delegate.
                    # They don't seem to forward the notifications that we want,
                    # so we need to take over (again).
                    self._next_delegate = delegate
                    NS.App.setDelegate_(self)

            def applicationDidFinishLaunching_(self, notification):
                print "applicationDidFinishLaunching:%s" % notification

                user_info = notification.userInfo()
                was_user_notification = user_info and user_info.objectForKey_("NSApplicationLaunchUserNotificationKey")
                if was_user_notification:
                    self.userNotificationCenter_didActivateNotification_(
                        NS.UserNotificationCenter.defaultUserNotificationCenter(),
                        notification
                    )

                if self._next_delegate:
                    self._next_delegate.applicationDidFinishLaunching_(notification)

            def userNotificationCenter_didDeliverNotification_(self, center, notification):
                print "userNotificationCenter_didDeliverNotification_"

            def userNotificationCenter_didActivateNotification_(self, center, notification):
                print "userNotificationCenter_didActivateNotification_"
                meta = notification.userInfo()
                if 'uitools' in meta:
                    print meta['uitools']
                
                # If you want to remove it:
                center.removeDeliveredNotification_(notification)

            def userNotificationCenter_shouldPresentNotification_(self, center, note):
                print "userNotificationCenter_shouldPresentNotification_"
                return True;

        def _replace_bundle_id(bundle_id='com.westernx.sgactions'):

            import ctypes
            C = ModuleProxy(['', 'c_'], [ctypes])

            capi = C.pythonapi

            # id objc_getClass(const char *name)
            capi.objc_getClass.restype = C.void_p
            capi.objc_getClass.argtypes = [C.char_p]

            # SEL sel_registerName(const char *str)
            capi.sel_registerName.restype = C.void_p
            capi.sel_registerName.argtypes = [C.char_p]

            def capi_get_selector(name):
                return C.void_p(capi.sel_registerName(name))

            # Method class_getInstanceMethod(Class aClass, SEL aSelector)
            # Will also search superclass for implementations.
            capi.class_getInstanceMethod.restype = C.void_p
            capi.class_getInstanceMethod.argtypes = [C.void_p, C.void_p]

            # void method_exchangeImplementations(Method m1, Method m2)
            capi.method_exchangeImplementations.restype = None
            capi.method_exchangeImplementations.argtypes = [C.void_p, C.void_p]


            #objc.lookUpClass("NSBundle")
            class NSBundle(objc.Category(NS.Bundle)):

                @objc.typedSelector(NS.Bundle.bundleIdentifier.signature)
                def uitoolsBundleIdentifier(self):
                    if self == NSBundle.mainBundle():
                        return "com.westernx.sgactions"
                    return self.uitoolsBundleIdentifier()

            class_ = capi.objc_getClass("NSBundle")
            old_method = capi.class_getInstanceMethod(class_, capi_get_selector("bundleIdentifier"))
            new_method = capi.class_getInstanceMethod(class_, capi_get_selector("uitoolsBundleIdentifier"))
            capi.method_exchangeImplementations(old_method, new_method)



if IS_LINUX:
    try:
        from gi.repository import GLib, Notify as LibNotify
    except ImportError:
        LibNotify = None
    else:
        LibNotify.init("uitools")


class NotifierFailed(RuntimeError):
    pass



_notifiers = []
class Notification(object):

    def notifier(availible):
        availible = bool(availible)
        def _notifier(func):
            func.is_availible = availible
            if availible:
                _notifiers.append(func)
            return func
        return _notifier

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

    def send(self, **kwargs):
        failures = []
        for notifier in self._notifiers:
            try:
                return notifier(self, **kwargs)
            except NotifierFailed as e:
                failures.append(e)
        raise NotifierFailed('; '.join(str(e) for e in failures))

    @notifier(IS_MACOS and NS)
    def send_via_notification_center(self):

        center = NS.UserNotificationCenter.defaultUserNotificationCenter()
        if not center:
            raise NotifierFailed('no notification center; is this not in a bundle?')

        notification = NS.UserNotification.alloc().init()

        notification.setTitle_(str(self.title))
        if self.subtitle:
            notification.setSubtitle_(str(self.subtitle))
        notification.setInformativeText_(str(self.message))

        notification.setUserInfo_({'uitools': 'this is where args and kwargs go'})

        if True: # More things we can do in the future:

            # This only works if _showsButtons (below) is not used.
            # If active, set*ButtonTitle does nothing.
            #notification.setHasReplyButton_(True)

            # This only works if we are set to be a banner (by the user via
            # System Preferences) and is overriden by the _showsButtons
            # private API below.
            #notification.setHasActionButton_(True)

            # These only work if we are set to be a batter (by the user via
            # System preferences) OR by the _showsButtons below. If not used,
            # they default to "Show" and "Close".
            #notification.setActionButtonTitle_("Action1")
            #notification.setOtherButtonTitle_("Action2")

            # Turn this into an "alert"; Private APIs FTW!
            # See: https://github.com/indragiek/NSUserNotificationPrivate
            if False and notification.respondsToSelector_("_showsButtons"):

                notification.setValue_forKey_(True, "_showsButtons")

            if False and notification.respondsToSelector_("_identityImage"):
                image1 = NS.Image.alloc().initWithContentsOfFile_('/home/mboers/Documents/textures/ash_uvgrid01.jpg')
                notification.setValue_forKey_(image1, "_identityImage")
                notification.setValue_forKey_(False, "_identityImageHasBorder")

            if True:
                # This works with all defaults, and is public!
                image2 = NS.Image.alloc().initWithContentsOfFile_('/home/mboers/Documents/textures/ash_uvgrid01.jpg')
                notification.setContentImage_(image2)

        center.setDelegate_(_Delegate.instance())
        center.scheduleNotification_(notification)

    @notifier(IS_MACOS)
    def send_via_terminal_notifier(self):
        argv = ['terminal-notifier',
            '-title', title,
            '-message', message,
            '-open', 'file://' + self.get_tempfile_path(),
        ]
        try:
            check_call(argv)
        except Exception as e:
            raise NotifierFailed('terminal-notifier failed: %s %s' % (e.__type_, e))

    @notifier(IS_MACOS)
    def send_via_osascript(self):

        # AppleScript works since 10.9.
        argv = ['osascript', '-e', 'display notification "%s" with title "%s"' % (
            message.replace('"', '\\"'),
            title.replace('"', '\\"'),
        )]
        try:
            check_call(argv)
        except Exception as e:
            raise NotifierFailed('osascript failed: %s %s' % (e.__type_, e))
    
    @notifier(IS_MACOS)
    def send_via_growlnotify(self):

        argv = ['growlnotify',
            '--name', 'Shotgun Action Dispatcher',
            '--title', title,
            '--message', message
        ]
        if self.sticky:
            argv.append('-s')
        try:
            check_call(argv)
        except Exception as e:
            raise NotifierFailed('growlnotify failed: %s %s' % (e.__type_, e))

    @notifier(IS_LINUX and LibNotify)
    def send_via_libnotify(self):
        # see: https://developer.gnome.org/libnotify/0.7/libnotify-notify.html
        # see: https://developer.gnome.org/libnotify/0.7/NotifyNotification.html

        # Can check LibNotify.get_server_caps() for a list of capabilities.
        print 'capabilities', LibNotify.get_server_caps()
        self._notification = notification = LibNotify.Notification.new(
            self.title,
            self.message,
            'folder-new'
        )
        
        # If this is "default", then it is the default action for clicking the notification.
        notification.add_action('default', 'Default Action', _on_action, 'on_action_payload')
        notification.add_action('not_default', 'Another Action', _on_action, 'another_payload')
        notification.connect('closed', _on_action)

        notification.set_timeout(5000) # 5s
        notification.show()

        # NOTE: This object NEEDS to be held onto for the callback to work.


    @notifier(IS_LINUX)
    def send_via_notify_send(self):

        argv = ['notify-send']
        if self.sticky:
            argv.extend(['-t', '3600000'])
        argv.extend([self.title, self.message])
        try:
            check_call(argv)
        except Exception as e:
            raise NotifierFailed('notify-send failed: %s %s' % (e.__type_, e))



Notification._notifiers = _notifiers
del _notifiers


def _on_action(*args, **kwargs):
    print 'action', args, kwargs

def main_bundle():
    import os
    import sys

    logfile = open('/tmp/uitools.notifications.test.log', 'a')
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

    print 'argv:', ' '.join(sys.argv)
    main()



def main():

    import argparse
    import time

    parser = argparse.ArgumentParser()
    parser.add_argument('--loop', action='store_true')
    parser.add_argument('--qt', action='store_true')
    args = parser.parse_args()


    if IS_MACOS:
        ns_app = NS.Application.sharedApplication()
        ns_app.setDelegate_(_Delegate.instance())        
        if not NS.UserNotificationCenter.defaultUserNotificationCenter():
            # If we do this, then we can't respond to our own events!
            _replace_bundle_id()

    if args.qt:

        from PyQt4 import QtCore, QtGui

        qt_app = QtGui.QApplication([])

        button = QtGui.QPushButton("HERE")
        @button.clicked.connect
        def on_button_clicked():
            Notification('Qt', 'You pressed the button in QT').send()
        button.show()

        qt_timer = QtCore.QTimer()
        qt_timer.setInterval(0)

    # Need to keep this around (for the libnotify handle).
    note = Notification('Test', 'This is a test.', subtitle='Subtitle')
    note.send_via_notification_center()


    if IS_MACOS:

        # You can actually do this for Qt or not, and either of them work.
        #NS.ApplicationMain(sys.argv)
        #ns_app.run()

        if not (args.loop or args.qt):

            print 'Manually catching events in order to get applicationDidFinishLaunching'
            # Thanks: http://www.cocoawithlove.com/2009/01/demystifying-nsapplication-by.html
            ns_app.finishLaunching()
            # pool = NS.AutoreleasePool.alloc().init()
            # We trigger the app to listen for events, even though it doesn't seem
            # that an "event" is what triggers applicationDidFinishLaunching.
            # We just need to keep waiting for events long enough for that to happen.
            event = ns_app.nextEventMatchingMask_untilDate_inMode_dequeue_(
                NS.AnyEventMask,
                NS.Date.dateWithTimeIntervalSinceNow_(0.1), # Must be non-zero
                NS.DefaultRunLoopMode,
                True
            )
            if event is not None:
                # This doesn't happen often, but lets give the event to the app
                # anyways (to be safe).
                ns_app.sendEvent_(event)
                ns_app.updateWindows()

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
