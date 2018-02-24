#!/usr/bin/env python
# encoding: UTF-8

try:
    from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QPushButton, QAction, QActionGroup, QTreeWidget, QTreeWidgetItem, QRadioButton, QFileDialog, QToolBar
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QIcon, QFont

except ImportError:
    from PyQt4.QtGui import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QPushButton, QAction, QIcon, QFont, QActionGroup, QTreeWidget, QTreeWidgetItem, QRadioButton, QFileDialog, QToolBar
    from PyQt4.QtCore import Qt


class PolyToolBar(QToolBar):
    """
    Provide the toolbar with all actions to load, build, correct, ... a polygon
    """

    def __init__(self, parent=None):
        """
        Initialize the widget itself and call super class to get the functionality of QToolBar.

        Parameters
        ----------
        parent: <__main__.GIMod object>
            Every widget that needs to be accessed is called in :class:`~GIMod`
        """
        super(PolyToolBar, self).__init__(parent)
        self.parent = parent

        self.setupTools()

    def setupTools(self):
        """Implement functionality to the toolbar."""
        # create a group for the image tools
        self.grp_imageTools = QActionGroup(self)
        self.acn_image = QAction(
            QIcon('icons/ic_image.svg'), 'image', self.grp_imageTools)
        self.acn_image.setToolTip(
            "Load image to set as model background or try to extract polygons from")

        # action to reset the figure and delete all created content
        self.acn_reset_figure = QAction(
            QIcon('icons/ic_reset.svg'), 'image', self.grp_imageTools)
        self.acn_reset_figure.setToolTip("Reset everything to nothing")
        self.acn_reset_figure.setEnabled(False)

        # create a real polygon (plc) if everything is ready
        self.acn_polygonize = QAction(
            QIcon('icons/ic_polygonize.svg'), 'image', self.grp_imageTools)
        self.acn_polygonize.setToolTip("polygonize the contours")
        self.acn_polygonize.setEnabled(False)

        # set the image as background for drawing trace
        self.acn_imageAsBackground = QCheckBox('as background')
        # self.acn_imageAsBackground.setEnabled(False)
        self.acn_imageAsBackground.setToolTip(
            "set the chosen image as background to paint your model")

        # the lower bound for the b/w threshold
        self.acn_imageThreshold1 = QSpinBox()
        self.acn_imageThreshold1.setRange(0, 254)
        self.acn_imageThreshold1.setValue(200)
        self.acn_imageThreshold1.setToolTip("bottom value for threshold")

        # the upper bound for the b/w threshold
        self.acn_imageThreshold2 = QSpinBox()
        self.acn_imageThreshold2.setRange(1, 255)
        self.acn_imageThreshold2.setValue(255)
        self.acn_imageThreshold2.setToolTip("top value for threshold")

        # the point density of each contour
        # this sets number of points that are being skipped in the path
        self.acn_imageDensity = QSpinBox()
        self.acn_imageDensity.setRange(1, 10)
        self.acn_imageDensity.setToolTip("set density of dots in polygon")

        # the polygons are ordered by area... so this allows to take one by one
        # into account getting smaller each step
        self.acn_imagePolys = QSpinBox()
        self.acn_imagePolys.setToolTip(
            "set the number of polygons used for model creation")

        # sort the widgets nicely in a layout
        acnBox = QHBoxLayout()
        acnBox.addWidget(self.acn_imageAsBackground)
        acnBox.addWidget(self.acn_imageThreshold1)
        acnBox.addWidget(self.acn_imageThreshold2)
        acnBox.addWidget(self.acn_imageDensity)
        acnBox.addWidget(self.acn_imagePolys)
        acnBox.setContentsMargins(0, 0, 0, 1)
        self.acnWidget = QWidget()
        self.acnWidget.setLayout(acnBox)
        self.acnWidget.setEnabled(False)

        # next group for the polyttols of GIMLi
        self.grp_polyTools = QActionGroup(self)
        # the button that allows to access the drawing of the world
        self.acn_world = QAction(
            QIcon('icons/ic_spanWorld.svg'),
            "Create your model world where everything happens",
            self.grp_polyTools, checkable=True)

        # the button that allows to access the drawing of a rectangle
        self.acn_rectangle = QAction(
            QIcon('icons/ic_spanRectangle.svg'),
            "Create a rectangle body",
            self.grp_polyTools, checkable=True)
        self.acn_rectangle.setEnabled(False)

        # the button that allows to access the drawing of a circle
        self.acn_circle = QAction(
            QIcon('icons/ic_spanCircle.svg'),
            "Create a circle body",
            self.grp_polyTools, checkable=True)
        self.acn_circle.setEnabled(False)

        # the button that allows to access the drawing of a line
        self.acn_line = QAction(
            QIcon('icons/ic_spanLine.png'),
            "Create a line by clicking",
            self.grp_polyTools, checkable=True)
        self.acn_line.setEnabled(False)

        # the button that allows to access the drawing of a random polygon
        self.acn_polygon = QAction(
            QIcon('icons/ic_spanPoly.svg'),
            "Create a polygon by clicking, finish with double click",
            self.grp_polyTools, checkable=True)
        self.acn_polygon.setEnabled(False)

        # action to marke each region's marker position.. those dots can be
        # dragged and will be checked for new positions
        self.acn_markerCheck = QAction(
            QIcon('icons/marker_check.svg'),
            "check and reset marker positions",
            self.grp_polyTools, checkable=True)
        self.acn_markerCheck.setEnabled(False)

        # action to turn on/off a grid. should help while creating the model
        self.acn_gridToggle = QAction(
            QIcon('icons/grid.svg'),
            "turn on and off a grid",
            None, checkable=True)

        # action to magnetize all grid lines
        self.acn_magnetizeGrid = QAction(
            QIcon('icons/grid_magnetize.svg'),
            "magnetize the grid junctions",
            None, checkable=True)
        self.acn_magnetizeGrid.setEnabled(False)

        # action to magnetize the vertices/nodes of every polygon
        self.acn_magnetizePoly = QAction(
            QIcon('icons/magnetize.svg'),
            "magnetize the polygons",
            None, checkable=True)
        self.acn_magnetizePoly.setEnabled(False)

        # add all actions and widgets to the toolbar
        self.addAction(self.acn_image)
        self.addWidget(self.acnWidget)
        # self.widgetAction = self.addWidget(acnWidget)
        # self.widgetAction.setVisible(False)
        self.addAction(self.acn_polygonize)
        self.addSeparator()
        self.addAction(self.acn_reset_figure)
        self.addSeparator()
        self.addAction(self.acn_world)
        self.addAction(self.acn_polygon)
        self.addAction(self.acn_rectangle)
        self.addAction(self.acn_circle)
        self.addAction(self.acn_line)
        self.addSeparator()
        self.addAction(self.acn_markerCheck)
        self.addSeparator()
        self.addAction(self.acn_gridToggle)
        self.addAction(self.acn_magnetizeGrid)
        self.addAction(self.acn_magnetizePoly)

        # set a iconsize!
        self.setIconSize(QSize(18, 18))


if __name__ == '__main__':
    pass
