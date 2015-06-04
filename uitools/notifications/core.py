#!/usr/bin/python

import json
import os
import site
import sys
import traceback


IS_MACOS = sys.platform == 'darwin'
IS_LINUX  = sys.platform.startswith('linux')

class NotifierFailed(RuntimeError):
    pass


try:
    if IS_MACOS:
        from .darwin import Notification
    elif IS_LINUX:
        from .linux import Notification
except ImportError:
    from .fallback import Notification


def _on_action(*args, **kwargs):
    print 'action', args, kwargs

