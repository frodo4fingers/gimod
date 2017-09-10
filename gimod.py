#!/usr/bin/env python
# encoding: UTF-8

try:
    from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QLineEdit,  QPushButton, QStatusBar, QToolBar, QTabWidget, QSplitter, QAction, QMessageBox, QFileDialog, QMenu
    from PyQt5.QtCore import QSize, Qt
    from PyQt5.QtGui import QIcon

except ImportError:
    from PyQt4.QtGui import QMainWindow, QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QLineEdit,  QPushButton, QStatusBar, QToolBar, QTabWidget, QSplitter, QAction, QMessageBox, QIcon, QFileDialog, QMenu
    from PyQt4.QtCore import QSize, Qt

import sys
import pygimli as pg
from pygimli.meshtools import createMesh, exportPLC, exportFenicsHDF5Mesh, readPLC
from pygimli.mplviewer import drawMeshBoundaries, drawMesh, drawPLC, drawModel

from core import Builder, ImageTools
from gui import InfoTree, MeshOptions, PlotWidget, PolyToolBar


class GIMod(QMainWindow):

    def __init__(self, parent=None):
        super(GIMod, self).__init__(parent)
        self.initUI()
        self.image_tools = ImageTools(self)

        # menu actions
        self.mb_aboutVerison.triggered.connect(self.aboutVersion)

        self.mb_open_file.triggered.connect(self.openAnyFile)
        self.mb_save_poly.triggered.connect(self.exportPoly)
        self.mb_save_mesh.triggered.connect(self.exportMesh)

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
        # self.info_tree.btn_export.clicked.connect(self.exportPoly)

    def initUI(self):
        """Set the GUI together from the other widgets."""
        # instanciate the status bar to prompt some information of what is
        # going on beneath the hood
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # instanciate the toolbar with the polytool functionality
        self.toolBar = PolyToolBar(self)
        self.addToolBar(self.toolBar)

        self.menubar = self.menuBar()
        # call the menu generation
        self.menuBarItems()

        menu_file = self.menubar.addMenu("&File")
        # menu_file_open = QMenu("&Open", self)
        # menu_file_open.addAction(self.mb_open_file)
        menu_file_save = QMenu("&Save", self)
        menu_file_save.addAction(self.mb_save_poly)
        menu_file_save.addAction(self.mb_save_mesh)

        menu_file.addAction(self.mb_open_file)
        menu_file.addSeparator()
        menu_file.addMenu(menu_file_save)

        menu_about = self.menubar.addMenu("&About")
        menu_about.addAction(self.mb_aboutVerison)

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
        tabBox.addTab(self.info_tree, "Polygons")
        tabBox.addTab(self.mesh_options, "Mesh Options")
        # tabBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        v_plotWidget = QVBoxLayout()
        v_plotWidget.addWidget(self.plotWidget)

        # tile the GUI in two resizable sides
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(tabBox)
        splitter.addWidget(self.plotWidget)

        self.setCentralWidget(splitter)

        self.setGeometry(200, 100, 1000, 600)
        # window name
        self.setWindowTitle("GIMod")
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.show()

    def menuBarItems(self):
        """Create all entries visible in the menubar and its submenus."""
        # instanciate entries for "About"
        self.mb_aboutVerison = QAction("Version", self)
        # instanciate entries for "File"
        # action to save a poly figure
        self.mb_save_poly = QAction(QIcon('icons/ic_save.svg'), '&Poly', self)
        self.mb_save_poly.setStatusTip("Save the created polygon file to a plc")
        self.mb_save_poly.setEnabled(False)
        # action to save a mesh
        self.mb_save_mesh = QAction(QIcon('icons/ic_save.svg'), '&Mesh', self)
        self.mb_save_mesh.setStatusTip("Save the generated mesh file")
        self.mb_save_mesh.setEnabled(False)
        # action to open a file
        self.mb_open_file = QAction(QIcon('icons/ic_open.svg'), "&Open File", self)
        self.mb_open_file.setStatusTip("Open a file and lets see if GIMod can handle it")

    def aboutVersion(self):
        with open('version.json') as v:
            content = v.read()
        QMessageBox.information(self, "About", content)

    def exportPoly(self):
        """Export the poly figure."""
        export_poly = QFileDialog.getSaveFileName(
            self, caption='Save Poly Figure')[0]

        # if export_poly:
        if export_poly.endswith('.poly'):
            exportPLC(self.builder.poly, export_poly)
        else:
            exportPLC(self.builder.poly, export_poly + '.poly')

    def exportMesh(self):
        """
            export the final mesh
        """
        export_mesh = QFileDialog.getSaveFileName(
            self, caption="Save Mesh")[0]
        print(export_mesh)
        # if export_poly:
        if export_mesh.endswith(".bms"):
            exportFenicsHDF5Mesh(self.mesh_options.mesh, export_mesh)
        else:
            exportFenicsHDF5Mesh(self.mesh_options.mesh, export_mesh + ".bms")

    def openAnyFile(self):
        """
        Open a qt filedialogbox and open a file.

        Todo
        ----
        + open a poly
            + strip down the polyfile to fill the treewidget with editable info
        + open a picture
        + open a mesh
        """
        to_open = QFileDialog.getOpenFileName(self, caption="Open File")[0]
        if to_open:
            self.builder.poly = readPLC(to_open)
            self.builder.drawPoly(to_merge=False)
        else:
            pass


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setApplicationName("GIMod")

    main = GIMod()
    main.show()

    sys.exit(app.exec_())
