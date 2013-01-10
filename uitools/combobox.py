from .qt import QtCore, QtGui


class ComboBox(QtGui.QComboBox):
    
    def itemData(self, *args):
        return self._cleanData(super(ComboBox, self).itemData(*args).toPyObject())
    
    def currentData(self):
        return self.itemData(self.currentIndex())
    
    def _cleanData(self, data):
        if isinstance(data, dict):
            return dict(self._cleanData(x) for x in data.iteritems())
        if isinstance(data, (tuple, list)):
            return type(data)(self._cleanData(x) for x in data)
        if isinstance(data, QtCore.QString):
            return unicode(data)
        return data
