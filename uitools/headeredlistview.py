from .qt import Q, qt2py
from . import roles


HeaderDisplayRole = roles.get_role('header')
HEADER_HEIGHT = 20


class HeaderedListView(Q.ListView):
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verticalScrollMode', self.ScrollPerPixel)
        super(HeaderedListView, self).__init__(*args, **kwargs)

        self.restoreAfterInitialize()

    def restoreAfterInitialize(self):
        self._delegate = Delegate()
        self.setItemDelegate(self._delegate)

        # Only marginally larger than the default 100.
        self.setMinimumWidth(120)

    def scrollContentsBy(self, x, y):
        super(HeaderedListView, self).scrollContentsBy(x, y)
        
        # Need to force a repaint on the top of the list for the headers.
        # Repaint twice the height of the headers plus a little padding for
        # the top two headers (which may move) and the little bit that may
        # be revealed by them moving.
        self.viewport().update(0, 0, self.width(), 2 * HEADER_HEIGHT + 2 + abs(y))

    def paintEvent(self, e):

        super(HeaderedListView, self).paintEvent(e)

        painter = Q.StylePainter(self.viewport())
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)

        option = Q.StyleOptionHeader()
        option.initFrom(self.viewport())
        option.state &= ~Q.Style.State_HasFocus
        option.textAlignment = Q.AlignCenter
        
        headers = []

        # Collect the headers.
        root = self.rootIndex()
        row = 0
        while True:
            child = self.model().index(row, 0, root)
            row += 1
            if not child.isValid():
                break
            header = Delegate._headerToDraw(child)
            if not header:
                continue

            rect = super(HeaderedListView, self).visualRect(child)
            rect.setHeight(HEADER_HEIGHT)

            headers.append((rect, header))

        # Stack all headers that would go out the top to the top of the
        # next header.
        for i in reversed(range(len(headers))):
            this_rect = headers[i][0]
            next_rect = headers[i + 1][0] if i + 1 < len(headers) else None
            if this_rect.top() >= 0:
                continue
            this_rect.moveTop(min(0, next_rect.top() - HEADER_HEIGHT if next_rect else 0))

        for rect, header in headers:
            if rect.bottom() < 0:
                continue
            option.text = header
            option.rect = rect.adjusted(0, 0, 1, 0)
            painter.drawControl(Q.Style.CE_Header, option)


    def visualRect(self, index):
        rect = super(HeaderedListView, self).visualRect(index)
        if Delegate._headerToDraw(index):
            rect.setTop(rect.top() + HEADER_HEIGHT)
        return rect


class Delegate(Q.StyledItemDelegate):
    
    @staticmethod
    def _indexHeader(index):
        header = index.data(HeaderDisplayRole)
        return qt2py(header)

    @classmethod
    def _headerToDraw(cls, index):
        this_header = cls._indexHeader(index)
        if not this_header:
            return
        prev_header = None
        if index.row() > 0:
            prev_header = cls._indexHeader(index.sibling(index.row() - 1, index.column()))
        if this_header != prev_header:
            return this_header

    def sizeHint(self, option, index):
        size = super(Delegate, self).sizeHint(option, index).expandedTo(
            Q.Size(1, 20))
        if self._headerToDraw(index):
            if index.data(Q.DisplayRole) is not None:
                size.setHeight(size.height() + HEADER_HEIGHT)
            else:
                size.setHeight(HEADER_HEIGHT)
        return size

    def paint(self, painter, options, index):
                
        style = Q.Application.style()
        style.drawPrimitive(Q.Style.PE_PanelItemViewRow, options, painter)

        options.rect.adjust(2, 0, 0, 0)
        super(Delegate, self).paint(painter, options, index)
        
        # Column view arrow when there are children.
        has_children = (options.state & Q.Style.State_Children or
            index.model().hasChildren(index))
        if has_children:
            options.rect.setLeft(options.rect.right() - 12)
            style.drawPrimitive(Q.Style.PE_IndicatorColumnViewArrow, options, painter)


if __name__ == '__main__':

    app = Q.Application([])

    dialog = Q.Dialog()
    dialog.setLayout(Q.VBoxLayout())

    widget = HeaderedListView()
    dialog.layout().addWidget(widget)

    delegate = Delegate()
    widget.setItemDelegate(delegate)

    model = Q.StandardItemModel(5, 1)
    widget.setModel(model)

    items = []

    for i, c in enumerate('ABcdEFGHIjkl' * 10):
        item = Q.StandardItem()
        items.append(item)

        item.setText(c)
        item.setData('Uppercase' if (c.upper() == c) else 'Lowercase', HeaderDisplayRole)

        model.setItem(i, 0, item)

    dialog.show()
    app.exec_()
