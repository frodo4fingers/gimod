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
# from mpl import Helper

# TODO: CLEAAAAAAAAAAAAAN THIS!!!!


class GIMod(QMainWindow):

    def __init__(self, parent=None):
        super(GIMod, self).__init__(parent)
        print(self)
        self.initUI()
        self.image_tools = ImageTools(self)

        # connect meshing options with their functions
        self.mesh_options.chbx_mesh_refine.stateChanged.connect(self.changedChbxMeshRefine)
        self.mesh_options.chbx_smooth.stateChanged.connect(self.changedChbxSmooth)
        self.mesh_options.chbx_switches.stateChanged.connect(self.changedChbxSwitches)
        self.mesh_options.chbx_mesh_attr.stateChanged.connect(self.showMesh)
        self.mesh_options.btn_mesh.clicked.connect(self.clickedBtnMesh)
        self.mesh_options.btn_mesh_export.clicked.connect(self.meshExport)

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

    def changedChbxMeshRefine(self):
        if self.chbx_mesh_refine.isChecked() is True:
            self.cbx_mesh_refine.setEnabled(True)
            self.mesh_refine = True
        else:
            self.cbx_mesh_refine.setEnabled(False)
            self.mesh_refine = False

    def changedChbxSmooth(self):
        if self.chbx_smooth.isChecked() is True:
            self.cbx_smooth.setEnabled(True)
            self.spb_smooth.setEnabled(True)
            # self.smooth = True
            # self.cbx_smooth = int(self.cbx_smooth.currentText())
            # self.spb_smooth = self.spb_smooth.value()
            # print("%i, %i" % (self.cbx_smooth, self.spb_smooth))
        else:
            self.cbx_smooth.setEnabled(False)
            self.spb_smooth.setEnabled(False)
            # self.smooth = True
            # self.cbx_smooth = None
            # self.spb_smooth = None
            # print("%i, %i" % (self.cbx_smooth, self.spb_smooth))

    def changedChbxSwitches(self):
        if self.chbx_switches.isChecked() is True:
            self.le_switches.setEnabled(True)
        else:
            self.le_switches.setEnabled(False)

    def clickedBtnMesh(self):
        if self.mesh_refine is False:
            self.refine_method = None
        elif self.mesh_refine is True and self.cbx_mesh_refine.currentText() == "quadratic":
            self.refine_method = "createP2"
        elif self.mesh_refine is True and self.cbx_mesh_refine.currentText() == "spatially":
            self.refine_method = "createH2"

        if self.chbx_smooth.isChecked() is False:
            self.smooth_method = None
        else:
            self.smooth_method = [
                int(self.cbx_smooth.currentText()), self.spb_smooth.value()]

        if self.chbx_switches.isChecked() is False:
            self.switches = None
        else:
            self.switches = self.le_switches.text()
            # TODO make th switches work -->
            # http://pygimli.org/_examples_auto/modelling/plot_hybrid-mesh-2d.html?highlight=switches

        self.statusBar.showMessage("generating mesh...")
        self.mesh = createMesh(self.builder.getPoly(), quality=self.spb_mesh_quality.value(
        ), area=self.spb_cell_area.value(), smooth=self.smooth_method, switches=self.switches)

        if self.mesh_refine is True and self.cbx_mesh_refine.currentText() == "quadratic":
            self.statusBar.showMessage("create quadratic...")
            self.mesh = self.mesh.createP2()
        elif self.mesh_refine is True and self.cbx_mesh_refine.currentText() == "spatially":
            self.statusBar.showMessage("create spatially...")
            self.mesh = self.mesh.createH2()

        self.statusBar.showMessage(str(self.mesh))
        self.btn_mesh_export.setEnabled(True)
        self.showMesh()

    def showMesh(self):
        self.plotWidget.axis.cla()
        if self.chbx_mesh_attr.isChecked() is True:
            self.regionGetAttributes()
            pg.show(self.mesh, pg.solver.parseArgToArray(self.attr_map, self.mesh.cellCount(
            ), self.mesh), ax=self.plotWidget.axis)
            pg.show(drawMeshBoundaries(self.plotWidget.axis, self.mesh,
                                       hideMesh=False), ax=self.plotWidget.axis, fillRegion=False)
        else:
            pg.show(self.mesh, ax=self.plotWidget.axis)

        self.plotWidget.axis.set_ylim(self.plotWidget.axis.get_ylim()[::-1])
        self.plotWidget.canvas.draw()

    def meshExport(self):
        """
            export the final mesh
        """
        export_mesh = QFileDialog.getSaveFileName(
            self, caption="Save Mesh")

        # if export_poly:
        if export_mesh.endswith(".bms"):
            writePLC(self.mesh, export_mesh)
        else:
            writePLC(self.mesh, export_mesh + ".bms")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setApplicationName("GIMod")

    main = GIMod()
    # main.resize(600, 600)
    main.show()

    sys.exit(app.exec_())
