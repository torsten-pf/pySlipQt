"""
A PyQt5 custom widget used by pySlipQt.

Used to display text.  The grid and components:

    +-----------------------------------------+
    |  <title>                                |
    |                                         |
    |                  +----------------+     |
    |       <label>    | <text>         |     |
    |                  +----------------+     |
    |                                         |
    +-----------------------------------------+

The constructor:

    dt = DisplayText(parent, title='', label='', textwidth=None, tooltip=None)

    where title      is the text to display at the top of the widget
          label      is the text to the left of the displayed <text>
          textwidth  is the width (in pixels) of the <text> field
          tooltip    is the text of a tooltip for the widget

Methods:

    dt.set_text("some text")
    dt.clear()

"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class DisplayText(QWidget):

    # some subwidget sizes
    LabelWidth = 20

    # styles strings
    TextStyle = ('QLabel { background-color: white; '
                          'border:1px solid rgb(128, 128, 128); '
                          'border-radius: 3px; }')
    LabelStyle = ('QLabel { background-color: white; '
                           'border:1px solid rgb(128, 128, 128); '
                           'border-radius: 3px; }')
#    GroupStyle = 'QGroupBox { background-color: rgb(230, 230, 230); border-radius: 3px; }'

#    LabelStyle = 'QLabel { background-color : #f0f0f0; border: 1px solid gray; border-radius: 3px; }'
    GroupStyle = ('QGroupBox { background-color: rgb(230, 230, 230); }'
                  'QGroupBox::title { subcontrol-origin: margin; '
                                 '    background-color: rgb(215, 215, 215); '
                                 '    border-radius: 3px; '
                                 '    padding: 2 2px; '
                                 '    color: black; }')

    def __init__(self, title, label, tooltip=None, text_width=None):
        super().__init__()

        lbl_label = QLabel(label)
        lbl_label.setFixedHeight(DisplayText.LabelWidth)

        self.lbl_text = QLabel()
        self.lbl_text.setStyleSheet(DisplayText.TextStyle)
        if text_width:
            self.lbl_text.setFixedWidth(text_width)
        self.lbl_text.setFixedHeight(20)

        option_box = QGroupBox(title)
        option_box.setStyleSheet(DisplayText.GroupStyle)

        box_layout = QHBoxLayout()
        box_layout.setContentsMargins(0, 0, 1, 1)

        box_layout.addWidget(lbl_label)
        box_layout.addWidget(self.lbl_text)
        box_layout.addStretch(1)

        option_box.setLayout(box_layout)

        layout = QVBoxLayout()
        layout.addWidget(option_box)

        self.setLayout(layout)

        if tooltip:
            self.setToolTip(tooltip)

    def set_text(self, text):
        """Set the text of the display field.

        text the text to show
        """

        self.lbl_text.setText(text)
