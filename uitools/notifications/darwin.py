
from metatools.apps.runtime import NS, replace_bundle_id


_delegate = None
def get_delegate():

    global _delegate
    if _delegate:
        return _delegate

    class WXNotificationDelegate(NS.Object):

        def _init(self):

            self._center = NS.UserNotificationCenter.defaultUserNotificationCenter()
            if not self._center:
                replace_bundle_id('com.westernx.uitools.notifications',
                    reason='to send notifications')
                self._center = NS.UserNotificationCenter.defaultUserNotificationCenter()
            if not self._center:
                raise RuntimeError('no notification center; is this not in a bundle?')

            self._next = self._center.delegate()
            self._center.setDelegate_(self)

        def userNotificationCenter_didDeliverNotification_(self, center, notification):
            pass
            # print "userNotificationCenter_didDeliverNotification_"

        def userNotificationCenter_didActivateNotification_(self, center, notification):
            pass
            # print "userNotificationCenter_didActivateNotification_"
            # meta = notification.userInfo()
            # if 'uitools' in meta:
            #     print meta['uitools']
            
            # If you want to remove it:
            center.removeDeliveredNotification_(notification)

        def userNotificationCenter_shouldPresentNotification_(self, center, note):
            # print "userNotificationCenter_shouldPresentNotification_"
            return True;

    _delegate = WXNotificationDelegate.alloc().init()
    _delegate._init()
    return _delegate


class Notification(object):

    def __init__(self, title=None, message=None, subtitle=None):

        if not (title or message):
            raise ValueError('please supply title or message')
        self.title = title
        self.subtitle = subtitle
        self.message = message

        self._sent = False

    def send(self):

        center = get_delegate()._center
        if not center:
            raise RuntimeError('WXNotificationDelegate._center is None')

        notification = NS.UserNotification.alloc().init()

        if self.title:
            notification.setTitle_(str(self.title))
        if self.subtitle:
            notification.setSubtitle_(str(self.subtitle))
        if self.message:
            notification.setInformativeText_(str(self.message))

        # notification.setUserInfo_({'uitools': 'this is where args and kwargs go in the future'})

        if False: # More things we can do in the future:

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

        center.scheduleNotification_(notification)

