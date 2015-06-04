import site

extras = '/System/Library/Frameworks/Python.framework/Versions/Current/Extras/lib/python'
site.addsitedir(extras)

from PyObjCTools import AppHelper
import AppKit
import CoreFoundation
import Foundation
import objc

from ..utils import ModuleProxy


NS = ModuleProxy(['NS'], [Foundation, AppKit])
CF = ModuleProxy(['CF'], [CoreFoundation])


class Delegate(NS.Object):

    _instance = None

    @classmethod
    def instance(cls):
        obj = cls._instance
        if not obj:
            obj = cls._instance = cls.alloc().init()
            obj._nextDelegate = None
        return obj

    def applicationWillFinishLaunching_(self, notification):
        print "applicationWillFinishLaunching:%s" % notification
        delegate = NS.App.delegate()
        if delegate is not self:
            # Seems like Qt has replaced us as the delegate.
            # They don't seem to forward the notifications that we want,
            # so we need to take over (again).
            self._nextDelegate = delegate
            NS.App.setDelegate_(self)

    def applicationDidFinishLaunching_(self, notification):
        print "applicationDidFinishLaunching:%s" % notification

        user_info = notification.userInfo()
        user_notification = user_info and user_info.objectForKey_("NSApplicationLaunchUserNotificationKey")
        if user_notification:
            self.userNotificationCenter_didActivateNotification_(
                NS.UserNotificationCenter.defaultUserNotificationCenter(),
                user_notification
            )

        if self._nextDelegate:
            self._nextDelegate.applicationDidFinishLaunching_(notification)

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


def _replace_bundle_id(bundle_id='com.westernx.uitools.notifications'):

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

    class NSBundle(objc.Category(NS.Bundle)):

        @objc.typedSelector(NS.Bundle.bundleIdentifier.signature)
        def uitoolsBundleIdentifier(self):
            if self == NSBundle.mainBundle():
                return bundle_id
            return self.uitoolsBundleIdentifier()

    class_ = capi.objc_getClass("NSBundle")
    old_method = capi.class_getInstanceMethod(class_, capi_get_selector("bundleIdentifier"))
    new_method = capi.class_getInstanceMethod(class_, capi_get_selector("uitoolsBundleIdentifier"))
    capi.method_exchangeImplementations(old_method, new_method)



class Notification(object):

    def __init__(self, title, message, subtitle=None):

        self.title = title
        self.subtitle = subtitle
        self.message = message

        self._sent = False

    def send(self):

        center = NS.UserNotificationCenter.defaultUserNotificationCenter()
        if not center:
            # If we do this, then we can't respond to our own events!
            print 'replacing bundle id'
            _replace_bundle_id()
            center = NS.UserNotificationCenter.defaultUserNotificationCenter()
        if not center:
            raise RuntimError('no notification center; is this not in a bundle?')

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

        center.setDelegate_(Delegate.instance())
        center.scheduleNotification_(notification)


def _setup():
    app = NS.Application.sharedApplication()
    app.setDelegate_(Delegate.instance())        

def _catch_startup_events():

    app = NS.App

    print 'Manually catching events in order to get applicationDidFinishLaunching'
    # Thanks: http://www.cocoawithlove.com/2009/01/demystifying-nsapplication-by.html

    # Trigger applicationWillFinishLaunching (among others).
    app.finishLaunching()

    # TODO: Should we do this?
    #pool = NS.AutoreleasePool.alloc().init()

    # We trigger the app to listen for events, even though it doesn't seem
    # that an "event" is what triggers applicationDidFinishLaunching.
    # We just need to keep waiting for events long enough for that to happen.
    event = app.nextEventMatchingMask_untilDate_inMode_dequeue_(
        NS.AnyEventMask,
        NS.Date.dateWithTimeIntervalSinceNow_(0.1), # Must be non-zero
        NS.DefaultRunLoopMode,
        True
    )

    if event is not None:
        # This doesn't happen often, but lets give the event to the app
        # anyways (to be safe).
        app.sendEvent_(event)
        app.updateWindows()
