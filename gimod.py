#!/usr/bin/env python
# encoding: UTF-8

try:
    from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QLineEdit,  QPushButton, QStatusBar, QToolBar, QTabWidget, QSplitter, QAction, QMessageBox
    from PyQt5.QtCore import QSize, Qt
    from PyQt5.QtGui import QIcon

except ImportError:
    from PyQt4.QtGui import QMainWindow, QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QLineEdit,  QPushButton, QStatusBar, QToolBar, QTabWidget, QSplitter, QAction, QMessageBox, QIcon
    from PyQt4.QtCore import QSize, Qt

import sys
import pygimli as pg
from pygimli.meshtools import createMesh, writePLC
from pygimli.mplviewer import drawMeshBoundaries, drawMesh, drawPLC, drawModel

from core import Builder, ImageTools
from gui import InfoTree, MeshOptions, PlotWidget, PolyToolBar


class GIMod(QMainWindow):

    def __init__(self, parent=None):
        super(GIMod, self).__init__(parent)
        self.initUI()
        self.image_tools = ImageTools(self)

        # menu actions
        self.acn_aboutVerison.triggered.connect(self.aboutVersion)

        # toolbar actions
        self.toolBar.acn_image.triggered.connect(self.image_tools.imagery)
        self.toolBar.acn_imageAsBackground.stateChanged.connect(self.image_tools.imageryBackground)
        self.toolBar.acn_imageThreshold1.valueChanged.connect(self.image_tools.updateImagery)
        self.toolBar.acn_imageThreshold2.valueChanged.connect(self.image_tools.updateImagery)
        self.toolBar.acn_imageDensity.valueChanged.connect(self.image_tools.updateImagery)
        self.toolBar.acn_imagePolys.valueChanged.connect(self.image_tools.polysFromImage)

        self.toolBar.acn_polygonize.triggered.connect(self.builder.formPolygonFromFigure)

        self.toolBar.acn_reset_figure.triggered.connect(self.builder.resetFigure)

        self.toolBar.acn_world.triggered.connect(self.builder.formPolyWorld)
        self.toolBar.acn_rectangle.triggered.connect(self.builder.formPolyRectangle)
        self.toolBar.acn_circle.triggered.connect(self.builder.formPolyCircle)
        self.toolBar.acn_line.triggered.connect(self.builder.formPolyLine)
        self.toolBar.acn_polygon.triggered.connect(self.builder.formPolygon)
        self.toolBar.acn_markerCheck.triggered.connect(self.builder.markersMove)

        self.toolBar.acn_gridToggle.triggered.connect(self.builder.toggleGrid)
        self.toolBar.acn_magnetizeGrid.triggered.connect(self.builder.magnetizeGrid)
        self.toolBar.acn_magnetizePoly.triggered.connect(self.builder.magnetizePoly)

        self.info_tree.btn_redraw.clicked.connect(self.info_tree.redrawTable)
        self.info_tree.btn_undo.clicked.connect(self.builder.undoPoly)
        self.info_tree.btn_redo.clicked.connect(self.builder.redoPoly)

    def initUI(self):
        """Set the GUI together from the other widgets."""
        # instanciate the status bar to prompt some information of what is
        # going on beneath the hood
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # instanciate the toolbar with the polytool functionality
        self.toolBar = PolyToolBar(self)
        self.addToolBar(self.toolBar)

        # initialize the plot widget where everything will be drawn
        self.plotWidget = PlotWidget(self)
        # self.plotWidget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.builder = Builder(self)

        # instanciate the info table for the polygons
        self.info_tree = InfoTree(self)

        # instanciate the mesh options tab to adjust the mesh parameters
        self.mesh_options = MeshOptions(self)

        tabBox = QTabWidget(self)
        tabBox.setTabPosition(QTabWidget.West)
        tabBox.addTab(self.info_tree, "poly properties")
        tabBox.addTab(self.mesh_options, "mesh options")
        # tabBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        v_plotWidget = QVBoxLayout()
        v_plotWidget.addWidget(self.plotWidget)

        # tile the GUI in two resizable sides
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(tabBox)
        splitter.addWidget(self.plotWidget)

        self.acn_aboutVerison = QAction("Version", self)

        menubar = self.menuBar()
        menu_file = menubar.addMenu("&About")
        menu_file.addAction(self.acn_aboutVerison)

        self.setCentralWidget(splitter)

        self.setGeometry(200, 100, 1000, 600)
        # window name
        self.setWindowTitle("GIMod")
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.show()

    def aboutVersion(self):
        with open('version.json') as v:
            content = v.read()
        QMessageBox.information(self, "About", content)

    def exportPoly(self):
        """Export the poly figure."""
        export_poly = QFileDialog.getSaveFileName(
            self, caption='Save Poly Figure')

        # if export_poly:
        if export_poly.endswith('.poly'):
            writePLC(self.poly, export_poly)
        else:
            writePLC(self.poly, export_poly + '.poly')


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setApplicationName("GIMod")

    main = GIMod()
    # main.resize(600, 600)
    main.show()

    sys.exit(app.exec_())
