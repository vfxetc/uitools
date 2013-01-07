from .qt import *


class CollapseToggle(QtGui.QCheckBox):

    def paintEvent(self, e):

        paint = QtGui.QStylePainter(self)
        option = QtGui.QStyleOptionButton()
        self.initStyleOption(option)

        # Paint the normal control.
        paint.drawControl(QtGui.QStyle.CE_CheckBox, option)

        # Re-use the style option, it contains enough info to make sure the
        # button is correctly checked
        option.rect = self.style().subElementRect(QtGui.QStyle.SE_CheckBoxIndicator, option, self)

        # Erase the checkbox...
        paint.save();
        px = QtGui.QPixmap(option.rect.width(), option.rect.height())
        px.fill(self, option.rect.left(), option.rect.top())
        brush = QtGui.QBrush(px)
        paint.fillRect(option.rect, brush)
        paint.restore()

        # ... and replace it with an arrow button.
        paint.drawPrimitive(QtGui.QStyle.PE_IndicatorArrowDown if self.isChecked() else QtGui.QStyle.PE_IndicatorArrowRight, option)
