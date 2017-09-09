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
    Provides the toolbar with all actions to load, build, correct etc. a polygon
    """

    def __init__(self, parent=None):
        super(PolyToolBar, self).__init__(parent)
        self.parent = parent

        self.setupTools()

        # connect actiosn to their functions
        self.acn_image.triggered.connect(self.parent.image_tools.imagery)
        self.acn_imageAsBackground.stateChanged.connect(self.parent.image_tools.imageryBackground)
        self.acn_imageThreshold1.valueChanged.connect(self.parent.image_tools.updateImagery)
        self.acn_imageThreshold2.valueChanged.connect(self.parent.image_tools.updateImagery)
        self.acn_imageDensity.valueChanged.connect(self.parent.image_tools.updateImagery)
        self.acn_imagePolys.valueChanged.connect(self.parent.image_tools.polysFromImage)

        self.acn_polygonize.triggered.connect(self.parent.builder.formPolygonFromFigure)

        self.acn_reset_figure.triggered.connect(self.parent.builder.resetFigure)

        self.acn_world.triggered.connect(self.parent.builder.formPolyWorld)
        self.acn_rectangle.triggered.connect(self.parent.builder.formPolyRectangle)
        self.acn_circle.triggered.connect(self.parent.builder.formPolyCircle)
        self.acn_line.triggered.connect(self.parent.builder.formPolyLine)
        self.acn_polygon.triggered.connect(self.parent.builder.formPolygon)
        self.acn_markerCheck.triggered.connect(self.parent.builder.markersMove)

        self.acn_gridToggle.triggered.connect(self.parent.builder.toggleGrid)
        self.acn_magnetizeGrid.triggered.connect(self.parent.builder.magnetizeGrid)
        self.acn_magnetizePoly.triggered.connect(self.parent.builder.magnetizePoly)

    def setupTools(self):
        """Implement functionality to the toolbar."""

        self.grp_imageTools = QActionGroup(self)
        self.acn_image = QAction(QIcon('icons/ic_image.svg'), 'image', self.grp_imageTools, checkable=True)
        self.acn_image.setToolTip("Load image to set as model background or try to extract polygons from")

        self.acn_reset_figure = QAction(QIcon('icons/ic_reset.svg'), 'image', self.grp_imageTools)
        self.acn_reset_figure.setToolTip("Reset everything to nothing")
        self.acn_reset_figure.setEnabled(False)

        self.acn_polygonize = QAction(QIcon('icons/ic_polygonize.svg'), 'image', self.grp_imageTools)
        self.acn_polygonize.setToolTip("polygonize the contours")
        self.acn_polygonize.setEnabled(False)

        self.acn_imageAsBackground = QCheckBox('as background')
        # self.acn_imageAsBackground.setEnabled(False)
        self.acn_imageAsBackground.setToolTip("set the chosen image as background to paint your model")
        self.acn_imageThreshold1 = QSpinBox()
        self.acn_imageThreshold1.setRange(0, 254)
        self.acn_imageThreshold1.setValue(200)
        self.acn_imageThreshold1.setToolTip("bottom value for threshold")
        self.acn_imageThreshold2 = QSpinBox()
        self.acn_imageThreshold2.setRange(1, 255)
        self.acn_imageThreshold2.setValue(255)
        self.acn_imageThreshold2.setToolTip("top value for threshold")
        self.acn_imageDensity = QSpinBox()
        self.acn_imageDensity.setRange(1, 10)
        self.acn_imageDensity.setToolTip("set density of dots in polygon")
        self.acn_imagePolys = QSpinBox()
        self.acn_imagePolys.setToolTip("set the number of polygons used for model creation")
        acnBox = QHBoxLayout()
        acnBox.addWidget(self.acn_imageAsBackground)
        acnBox.addWidget(self.acn_imageThreshold1)
        acnBox.addWidget(self.acn_imageThreshold2)
        acnBox.addWidget(self.acn_imageDensity)
        acnBox.addWidget(self.acn_imagePolys)
        acnBox.setContentsMargins(0, 0, 0, 1)
        acnWidget = QWidget()
        acnWidget.setLayout(acnBox)

        self.grp_polyTools = QActionGroup(self)
        self.acn_world = QAction(QIcon('icons/ic_spanWorld.svg'), 'world', self.grp_polyTools, checkable=True)
        self.acn_world.setToolTip("Create your model world where everything happens")

        self.acn_rectangle = QAction(QIcon('icons/ic_spanRectangle.svg'), 'rectangle', self.grp_polyTools, checkable=True)
        self.acn_rectangle.setToolTip("Create a rectangle body")
        self.acn_rectangle.setEnabled(False)

        self.acn_circle = QAction(QIcon('icons/ic_spanCircle.svg'), 'circle', self.grp_polyTools, checkable=True)
        self.acn_circle.setToolTip("Create a circle body")
        self.acn_circle.setEnabled(False)

        self.acn_line = QAction(QIcon('icons/ic_spanLine.png'), 'line', self.grp_polyTools, checkable=True)
        self.acn_line.setToolTip("Create a line by clicking")
        self.acn_line.setEnabled(False)

        self.acn_polygon = QAction(QIcon('icons/ic_spanPoly.svg'), 'polygon', self.grp_polyTools, checkable=True)
        self.acn_polygon.setToolTip("Create a polygon by clicking, finish with double click")
        self.acn_polygon.setEnabled(False)

        self.acn_markerCheck = QAction(QIcon('icons/marker_check.svg'), 'marker', self.grp_polyTools, checkable=True)
        self.acn_markerCheck.setToolTip("check and reset marker positions")
        self.acn_markerCheck.setEnabled(False)

        # self.grp_gridTools = QActionGroup(self)
        self.acn_gridToggle = QAction(QIcon('icons/grid.svg'), 'grid', None, checkable=True)
        self.acn_gridToggle.setToolTip("turn on and off a grid")
        self.acn_gridToggle.setEnabled(False)

        self.acn_magnetizeGrid = QAction(QIcon('icons/grid_magnetize.svg'), 'magnetizeGrid', None, checkable=True)
        self.acn_magnetizeGrid.setToolTip("magnetize the grid junctions")
        self.acn_magnetizeGrid.setEnabled(False)

        self.acn_magnetizePoly = QAction(QIcon('icons/magnetize.svg'), 'magnetizePoly', None, checkable=True)
        self.acn_magnetizePoly.setToolTip("magnetize the polygons")
        self.acn_magnetizePoly.setEnabled(False)

        self.addAction(self.acn_image)
        self.widgetAction = self.addWidget(acnWidget)
        self.widgetAction.setVisible(False)
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

        self.setIconSize(QSize(18, 18))
