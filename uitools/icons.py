import os

from .qt import Qt, QtGui


# THIS IS NOT IN A USABLE STATE!
raise ImportError(__name__)


_icons_by_name = {}
def icon(name, size=None, as_icon=False):
    
    try:
        icon = _icons_by_name[name]
    except KeyError:
    
        path = os.path.abspath(os.path.join(__file__, 
            '..', '..', '..',
            'art', 'icons', name + (os.path.splitext(name)[1] or '.png')
        ))

        if os.path.exists(path):
            icon = QtGui.QPixmap(path)
        else:
            icon = None
    
        _icons_by_name[name] = icon
    
    if icon and size:
        icon = icon.scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    
    if icon and as_icon:
        icon = QtGui.QIcon(icon)
    
    return icon