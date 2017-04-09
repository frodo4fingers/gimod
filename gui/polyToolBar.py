#!/usr/bin/env python
# encoding: UTF-8

try:
    from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QPushButton, QAction, QActionGroup, QTreeWidget, QTreeWidgetItem, QRadioButton, QFileDialog, QToolBar
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QIcon, QFont

except ImportError:
    from PyQt4.QtGui import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QPushButton, QAction, QIcon, QFont, QActionGroup, QTreeWidget, QTreeWidgetItem, QRadioButton, QFileDialog, QToolBar
    from PyQt4.QtCore import Qt


class PolyToolBar(QToolBar):
    """
        Provides the toolbar with all actions to load, build, correct etc. a polygon
    """

    def __init__(self, parent=None):
        super(PolyToolBar, self).__init__(parent)

        self.setupTools()

    def setupTools(self):

        self.acn_image = QAction(QIcon('icons/ic_image.svg'), 'image', None)
        self.acn_image.setToolTip("Load image to set as model background or try to extract polygons from")
        self.acn_image.setCheckable(True)

        self.addAction(self.acn_image)
