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
from gui import PlotWidget, PolyToolBar
from mpl import Helper

# TODO: CLEAAAAAAAAAAAAAN THIS!!!!


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.initUI()
        self.image_tools = ImageTools(self)
        # self.mpl_helper = Helper(self)

        ''' connect the buttons with their functions '''

        self.chbx_mesh_refine.stateChanged.connect(self.changedChbxMeshRefine)
        self.chbx_smooth.stateChanged.connect(self.changedChbxSmooth)
        self.chbx_switches.stateChanged.connect(self.changedChbxSwitches)
        self.chbx_mesh_attr.stateChanged.connect(self.showMesh)
        self.btn_mesh.clicked.connect(self.clickedBtnMesh)
        self.btn_mesh_export.clicked.connect(self.meshExport)
        # menu actions
        self.acn_aboutVerison.triggered.connect(self.aboutVersion)

        # toolbar actions
        self.toolBar.acn_image.triggered.connect(self.image_tools.imagery)
        self.toolBar.acn_imageAsBackground.stateChanged.connect(self.image_tools.imageryBackground)
        self.toolBar.acn_imageThreshold1.valueChanged.connect(self.image_tools.updateImagery)
        self.toolBar.acn_imageThreshold2.valueChanged.connect(self.image_tools.updateImagery)
        self.toolBar.acn_imageDensity.valueChanged.connect(self.image_tools.updateImagery)
        self.toolBar.acn_imagePolys.valueChanged.connect(self.image_tools.updateImagery)

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


    def initUI(self):

        # ####################################################################################### #
        # TAB MESH OPTIONS                                     #
        self.la_mesh_quality = QLabel("Mesh Quality:")
        self.spb_mesh_quality = QDoubleSpinBox(self)
        self.spb_mesh_quality.setMinimum(30.0)
        self.spb_mesh_quality.setMaximum(34.0)
        self.spb_mesh_quality.setValue(30.0)
        self.spb_mesh_quality.setSingleStep(0.1)

        self.la_cell_area = QLabel("max. cell area:")
        self.spb_cell_area = QDoubleSpinBox(self)
        self.spb_cell_area.setValue(0.0)
        self.spb_cell_area.setSingleStep(0.01)

        self.la_mesh_refine = QLabel("Refinement:")
        self.cbx_mesh_refine = QComboBox()
        self.cbx_mesh_refine.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cbx_mesh_refine.setEnabled(False)
        self.chbx_mesh_refine = QCheckBox()
        self.cbx_mesh_refine.addItem("quadratic")
        self.cbx_mesh_refine.addItem("spatially")
        self.mesh_refine = False

        self.la_smooth = QLabel("Smooth:")
        self.chbx_smooth = QCheckBox()
        self.cbx_smooth = QComboBox()
        self.cbx_smooth.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cbx_smooth.setToolTip("1 node center\n2 weighted node center")
        self.cbx_smooth.setEnabled(False)
        # self.cbx_smooth.addItem("0")
        self.cbx_smooth.addItem("1")
        self.cbx_smooth.addItem("2")
        self.spb_smooth = QSpinBox()
        self.spb_smooth.setToolTip("number of iterations")
        self.spb_smooth.setEnabled(False)
        self.spb_smooth.setMinimum(1)
        self.spb_smooth.setValue(5)

        self.la_switches = QLabel("Switches:")
        self.chbx_switches = QCheckBox()
        self.le_switches = QLineEdit("-pzeAfaq31")
        self.le_switches.setEnabled(False)
        self.switches = None

        self.la_mesh_show_attr = QLabel("Show Attributes:")
        self.chbx_mesh_attr = QCheckBox()

        self.btn_mesh = QPushButton("mesh")
        self.btn_mesh.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.btn_mesh_export = QPushButton()
        self.btn_mesh_export.setToolTip("save as *.bms")
        self.btn_mesh_export.setIcon(QIcon("icons/ic_save_black_24px.svg"))
        self.btn_mesh_export.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.btn_mesh_export.setEnabled(False)
        # labels stacked in vbox
        vbox_mesh_labels = QVBoxLayout()
        vbox_mesh_labels.addWidget(self.la_mesh_quality)
        vbox_mesh_labels.addWidget(self.la_cell_area)
        vbox_mesh_labels.addWidget(self.la_mesh_refine)
        vbox_mesh_labels.addWidget(self.la_smooth)
        vbox_mesh_labels.addWidget(self.la_switches)
        vbox_mesh_labels.addWidget(self.la_mesh_show_attr)
        # rest organized in layout boxes
        vbox_mesh_params = QVBoxLayout()
        vbox_mesh_params.addWidget(self.spb_mesh_quality)
        vbox_mesh_params.addWidget(self.spb_cell_area)
        hbox_mesh_refine = QHBoxLayout()
        hbox_mesh_refine.addWidget(self.chbx_mesh_refine)
        hbox_mesh_refine.addWidget(self.cbx_mesh_refine)
        vbox_mesh_params.addLayout(hbox_mesh_refine)
        hbox_mesh_smooth = QHBoxLayout()
        hbox_mesh_smooth.addWidget(self.chbx_smooth)
        hbox_mesh_smooth.addWidget(self.cbx_smooth)
        hbox_mesh_smooth.addWidget(self.spb_smooth)
        vbox_mesh_params.addLayout(hbox_mesh_smooth)
        # TODO
        # hbox_mesh_switches = QHBoxLayout()
        # hbox_mesh_switches.addWidget(self.chbx_switches)
        # hbox_mesh_switches.addWidget(self.le_switches)
        # vbox_mesh_params.addLayout(hbox_mesh_switches)
        hbox_mesh_attr = QHBoxLayout()
        hbox_mesh_attr.addWidget(self.chbx_mesh_attr)
        hbox_mesh_attr.addStretch(1)
        vbox_mesh_params.addLayout(hbox_mesh_attr)

        hbox_mesh = QHBoxLayout()
        hbox_mesh.addLayout(vbox_mesh_labels)
        hbox_mesh.addLayout(vbox_mesh_params)

        hbox_mesh_n_export = QHBoxLayout()
        hbox_mesh_n_export.addWidget(self.btn_mesh)
        hbox_mesh_n_export.addWidget(self.btn_mesh_export)

        vbox_mesh = QVBoxLayout()
        vbox_mesh.addLayout(hbox_mesh)
        vbox_mesh.addLayout(hbox_mesh_n_export)
        vbox_mesh.addStretch(1)

        mesh_widget = QWidget()
        mesh_widget.setLayout(vbox_mesh)

        # ####################################################################################### #
        # SET UP TOOLBOX                                     #
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # instanciate empty toolbar that will be equipped elsewhere
        # self.toolBar = QToolBar(self)
        self.toolBar = PolyToolBar(self)
        # self.toolBar.setIconSize(QSize(18, 18))
        self.addToolBar(self.toolBar)

        # initialize the plot widget
        self.plotWidget = PlotWidget(self)
        self.plotWidget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.builder = Builder(self)
        tabBox = QTabWidget(self)
        tabBox.setTabPosition(QTabWidget.West)
        # tabBox.addTab(file_widget, "start with sketch")
        tabBox.addTab(self.builder, "poly properties")
        tabBox.addTab(mesh_widget, "mesh options")
        tabBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        v_plotWidget = QVBoxLayout()
        v_plotWidget.addWidget(self.plotWidget)

        # ### split this
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
    app.setApplicationName("MainWindow")

    main = MainWindow()
    # main.resize(600, 600)
    main.show()

    sys.exit(app.exec_())
