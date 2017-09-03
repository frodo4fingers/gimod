#!/usr/bin/env python
# encoding: UTF-8

import matplotlib
try:
    matplotlib.use("Qt5Agg")
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
    from PyQt5.QtCore import QSize
    from PyQt5.QtGui import QIcon

except ImportError:
    matplotlib.use("Qt4Agg")
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
    from PyQt4.QtGui import QWidget, QApplication, QVBoxLayout, QIcon
    from PyQt4.QtCore import QSize

from matplotlib.figure import Figure


# class PlotToolbar(NavigationToolbar):
#
#     def __init__(self, plot, parent=None):
#         # https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/backends/backend_qt5.py
#         self.toolitems = (
#             ('Home', 'Reset original view', 'home', 'home'),
#             # (None, None, None, None),
#             ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
#             ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
#             # (None, None, None, None),
#             ('Save', 'Save the figure', 'filesave', 'save_figure'),
#             )
#
#         NavigationToolbar.__init__(self, plot, parent=None, coordinates=False)


class PlotWidget(QWidget):
    """
        Provides the standard matplotlib plot
    """

    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()
        self.figure.subplots_adjust(
            left=0.05, right=0.95, bottom=0.05, top=0.95)
        self.axis = self.figure.add_subplot(111)

        self.axis.set_xlabel('x')
        self.axis.set_ylabel('z')
        # self.axis.set_ylim(self.axis.get_ylim()[::-1])
        self.axis.set_aspect('equal')
        self.canvas = FigureCanvas(self.figure)
        self.resetFigure()

        # self.toolbar = PlotToolbar(self.canvas, self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setFixedHeight(30)
        self.toolbar.setIconSize(QSize(18, 18))
        # self.toolbar.setContentsMargins(0, 0, 0, 0)

        # add buttons
        # self.btn_zoom_in = QToolButton()
        # self.btn_zoom_in.setIcon(QIcon("icons/ic_zoom_in_black_24px.svg"))
        # self.btn_zoom_in.setToolTip("zoom in")
        # self.btn_zoom_in.clicked.connect(self.zoomIn)
        # self.btn_zoom_out = QToolButton()
        # self.btn_zoom_out.setIcon(QIcon("icons/ic_zoom_out_black_24px.svg"))
        # self.btn_zoom_out.setToolTip("zoom out")
        # self.btn_zoom_out.clicked.connect(self.zoomOut)
        # self.toolbar.addWidget(self.btn_zoom_in)
        # self.toolbar.addWidget(self.btn_zoom_out)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.setMargin(0)
        self.setLayout(layout)

    # def zoomOut(self):
    #     """
    #         zoom Out of the current dimension
    #     """
    #     x_dim = self.axis.get_xlim()
    #     x_dist = abs(x_dim[1] - x_dim[0])
    #     y_dim = self.axis.get_ylim()
    #     y_dist = abs(y_dim[1] - y_dim[0])
    #
    #     self.axis.set_xlim(x_dim[0] - 0.1*x_dist, x_dim[1] + 0.1*x_dist)
    #     self.axis.set_ylim(y_dim[0] - 0.1*y_dist, y_dim[1] + 0.1*y_dist)
    #     self.canvas.draw()
    #
    # def zoomIn(self):
    #     """
    #         zoom In of the current dimension
    #     """
    #     x_dim = self.axis.get_xlim()
    #     x_dist = abs(x_dim[1] - x_dim[0])
    #     y_dim = self.axis.get_ylim()
    #     y_dist = abs(y_dim[1] - y_dim[0])
    #
    #     self.axis.set_xlim(x_dim[0] + 0.1*x_dist, x_dim[1] - 0.1*x_dist)
    #     self.axis.set_ylim(y_dim[0] + 0.1*y_dist, y_dim[1] - 0.1*y_dist)
    #     self.canvas.draw()

    def resetFigure(self):
        """Set contents margin to start layout after clearing the figures contents."""
        self.axis.cla()
        self.axis.set_xlim(-1, 1)
        self.axis.set_ylim(-1, 1)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    ex = PlotWidget()
    ex.show()
    sys.exit(app.exec_())
