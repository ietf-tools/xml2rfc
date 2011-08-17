""" This is a python implementation of QT's line editor tutorial

    http://doc.trolltech.com/4.6/widgets-codeeditor.html
"""

# PyQT modules
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class LineArea(QWidget):
    # Gutter widget for line numbers
    def __init__(self, editor):
        # Super
        QWidget.__init__(self, editor)
        self.editor = editor
    
    def sizeHint(self, *args, **kwargs):
        return QSize(self.editor.lineAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineAreaPaintEvent(event)


class LinedEditor(QPlainTextEdit):
    # Custom QTextEdit which supports line highlighting and line numbers
    def __init__(self, parent=None):
        # Super
        QPlainTextEdit.__init__(self, parent)
        
        # Default settings
        self.enableLineNumbers = True
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setFrameShape(QFrame.NoFrame)
        
        # Create line number widget
        self.lineArea = LineArea(self)

        # Connect relevant signals to editor
        self.connect(self, SIGNAL('blockCountChanged(int)'), \
                     self.updateLineAreaWidth)
        self.connect(self, SIGNAL('updateRequest(QRect, int)'), \
                     self.updateLineArea)
#        self.connect(self, SIGNAL('cursorPositionChanged()'), \
#                     self.highlightCurrentLine)
        
        # Initialize
        self.updateLineAreaWidth(0)
    
    def resizeEvent(self, event):
        # Resize line area as well
        QPlainTextEdit.resizeEvent(self, event)
        rect = self.contentsRect()
        self.lineArea.setGeometry(QRect(rect.left(), rect.top(), \
                                        self.lineAreaWidth(), rect.height()))

    def lineAreaWidth(self):
        # Return a gutter width of 4 chars
        if self.enableLineNumbers:
            fm = self.fontMetrics()
            return 4 + fm.width(QChar('9')) * 4
        else:
            return 0

    def updateLineAreaWidth(self, blocks):
        # Make space for the gutter
        self.setViewportMargins(self.lineAreaWidth(), 0, 0, 0)
    
    def updateLineArea(self, rect, dy):
        # Respond to a scroll event
        if dy:
            self.lineArea.scroll(0, dy)
        else:
            self.lineArea.update(0, rect.y(), \
                                 self.lineArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineAreaWidth(0)
    
    def highlightCurrentLine(self):
        # Draw a background on the line of the cursor
        extraSelections = self.extraSelections()
        selection = QTextEdit.ExtraSelection()
        lineColor = QColor(Qt.red).lighter(160)
        selection.format.setBackground(lineColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        extraSelections.append(selection)
        self.setExtraSelections(extraSelections)
    
    def lineAreaPaintEvent(self, event):
        # Draw gutter area
        painter = QPainter(self.lineArea)
        painter.fillRect(event.rect(), QColor('#CEF2FF'))

        # Match editor font
        painter.setFont(self.font())

        # Calculate geometry
        firstBlock = self.firstVisibleBlock()
        blockNumber = firstBlock.blockNumber()
        top = self.blockBoundingGeometry(firstBlock).\
              translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(firstBlock).height()

        # Draw line numbers
        block = firstBlock
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                num = QString(str(blockNumber + 1))
                painter.setPen(Qt.black)
                painter.drawText(-1, top, self.lineArea.width(), \
                                 self.fontMetrics().height(), \
                                 Qt.AlignRight, num)

            # Increment
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber = blockNumber + 1
