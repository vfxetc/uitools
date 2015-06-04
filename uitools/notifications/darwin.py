from metatools.apps.runtime import NS, replace_bundle_id, Delegate


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
            replace_bundle_id()
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

