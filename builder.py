#!/usr/bin/env python
# encoding: UTF-8

""" class for tab with main model builder components """
from PyQt4 import QtGui

class Builder(QtGui.QWidget):

    def __init__(self, parent=None):
        # stuff
        super(Builder, self).__init__(parent)
        self.initLayout()

    def initLayout(self):
        """
            initiate the widget
        """

        self.btn_circle = QtGui.QPushButton("A")
        self.btn_circle.setCheckable(True)

        buttons_grid = QtGui.QGridLayout()
        buttons_grid.addWidget(self.btn_circle, 1, 0, 1, 1)

        builder_widget = QtGui.QWidget(self)
        builder_widget.setLayout(buttons_grid)
