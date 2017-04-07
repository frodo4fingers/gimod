#!/usr/bin/env python
# encoding: UTF-8

import sys
import matplotlib
try:
    matplotlib.use("Qt5Agg")
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QLineEdit,  QPushButton, QStatusBar, QToolBar, QTabWidget, QSplitter, QAction, QMessageBox
    from PyQt5.QtCore import QSize, Qt
    from PyQt5.QtGui import QIcon

except ImportError:
    matplotlib.use("Qt4Agg")
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
    from PyQt4.QtGui import QMainWindow, QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QLineEdit,  QPushButton, QStatusBar, QToolBar, QTabWidget, QSplitter, QAction, QMessageBox, QIcon
    from PyQt4.QtCore import QSize, Qt

from matplotlib.figure import Figure
from matplotlib import patches
import matplotlib.pyplot as plt

import pygimli as pg
from pygimli.meshtools import polytools as plc
from pygimli.meshtools import createMesh, writePLC
from pygimli.mplviewer import drawMeshBoundaries, drawMesh, drawPLC, drawModel

from core import Builder

# TODO: CLEAAAAAAAAAAAAAN THIS!!!!


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

    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()
        self.figure.subplots_adjust(
            left=0.05, right=0.95, bottom=0.05, top=0.95)
        self.axis = self.figure.add_subplot(111)

        self.axis.set_xlabel("x")
        self.axis.set_ylabel("z")
        self.axis.set_ylim(self.axis.get_ylim()[::-1])
        self.axis.set_aspect('equal')
        self.canvas = FigureCanvas(self.figure)

        # self.toolbar = PlotToolbar(self.canvas, self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setIconSize(QSize(18, 18))
        self.toolbar.setContentsMargins(0, 0, 0, 0)

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


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.initUI()

        ''' connect the buttons with their functions '''

        self.chbx_mesh_refine.stateChanged.connect(self.changedChbxMeshRefine)
        self.chbx_smooth.stateChanged.connect(self.changedChbxSmooth)
        self.chbx_switches.stateChanged.connect(self.changedChbxSwitches)
        self.chbx_mesh_attr.stateChanged.connect(self.showMesh)
        self.btn_mesh.clicked.connect(self.clickedBtnMesh)
        self.btn_mesh_export.clicked.connect(self.meshExport)
        # menu actions
        self.acn_aboutVerison.triggered.connect(self.aboutVersion)

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
        self.toolBar = QToolBar(self)
        self.toolBar.setIconSize(QSize(18, 18))
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
