
from gi.repository import GLib, Notify as LibNotify


class Notification(object):

    def __init__(self, title, message, subtitle=None, sticky=False):
        self.title = title
        self.subtitle = subtitle
        self.message = message
        self.sticky = sticky
        self._sent = False

    def send(self):

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


