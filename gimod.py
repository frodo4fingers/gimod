#!/usr/bin/env python
# encoding: UTF-8

import numpy as np
# from sklearn.neighbors import KDTree
# from scipy.spatial import KDTree
import sys
import cv2

import matplotlib
matplotlib.use("Qt4Agg")
from matplotlib.figure import Figure
# from matplotlib import pyplot as plt
from matplotlib import patches
# from matplotlib.widgets import RectangleSelector
from matplotlib.patches import Polygon as mpl_polygon
# from matplotlib.patches import Rectangle
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from PyQt4 import QtGui, QtCore

import pygimli as pg
from pygimli.meshtools import polytools as plc
from pygimli.meshtools import createMesh, writePLC
from pygimli.mplviewer import drawMeshBoundaries, drawMesh, drawPLC, drawModel

from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt

from collections import defaultdict, Counter
from builder import Builder
from regions import RegionQuickCheck
from mpl import DraggablePoint

# TODO: CLEAAAAAAAAAAAAAN THIS!!!!


class PlotToolbar(NavigationToolbar):

    def __init__(self, plot, parent=None):
        # https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/backends/backend_qt5.py
        self.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            # (None, None, None, None),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            ('Zoom', 'Zoom to recta ngle', 'zoom_to_rect', 'zoom'),
            # (None, None, None, None),
            ('Save', 'Save the figure', 'filesave', 'save_figure'),
            )

        NavigationToolbar.__init__(self, plot, parent=None, coordinates=False)


class PlotWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()
        self.figure.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)
        self.axis = self.figure.add_subplot(111)

        self.axis.set_xlabel("x")
        self.axis.set_ylabel("z")
        self.axis.set_ylim(self.axis.get_ylim()[::-1])
        self.canvas = FigureCanvas(self.figure)

        self.toolbar = PlotToolbar(self.canvas, self)
        self.toolbar.setIconSize(QtCore.QSize(18, 18))
        self.toolbar.setContentsMargins(0, 0, 0, 0)

        # add buttons
        self.btn_zoom_in = QtGui.QToolButton()
        self.btn_zoom_in.setIcon(QtGui.QIcon("material/ic_zoom_in_black_24px.svg"))
        self.btn_zoom_in.setToolTip("zoom in")
        self.btn_zoom_in.clicked.connect(self.zoomIn)
        self.btn_zoom_out = QtGui.QToolButton()
        self.btn_zoom_out.setIcon(QtGui.QIcon("material/ic_zoom_out_black_24px.svg"))
        self.btn_zoom_out.setToolTip("zoom out")
        self.btn_zoom_out.clicked.connect(self.zoomOut)
        self.toolbar.addWidget(self.btn_zoom_in)
        self.toolbar.addWidget(self.btn_zoom_out)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        layout.setMargin(0)
        self.setLayout(layout)

    def zoomOut(self):
        """
            zoom Out of the current dimension
        """
        x_dim = self.axis.get_xlim()
        x_dist = abs(x_dim[1] - x_dim[0])
        y_dim = self.axis.get_ylim()
        y_dist = abs(y_dim[1] - y_dim[0])

        self.axis.set_xlim(x_dim[0] - 0.1*x_dist, x_dim[1] + 0.1*x_dist)
        self.axis.set_ylim(y_dim[0] - 0.1*y_dist, y_dim[1] + 0.1*y_dist)
        self.canvas.draw()

    def zoomIn(self):
        """
            zoom In of the current dimension
        """
        x_dim = self.axis.get_xlim()
        x_dist = abs(x_dim[1] - x_dim[0])
        y_dim = self.axis.get_ylim()
        y_dist = abs(y_dim[1] - y_dim[0])

        self.axis.set_xlim(x_dim[0] + 0.1*x_dist, x_dim[1] - 0.1*x_dist)
        self.axis.set_ylim(y_dim[0] + 0.1*y_dist, y_dim[1] - 0.1*y_dist)
        self.canvas.draw()


class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.initUI()

        """ connect the buttons with their functions """
        self.btn_file.clicked.connect(self.chooseOpenSketch)

        self.sld_min.valueChanged.connect(self.movedSldMin)
        self.sld_min.sliderReleased.connect(self.imageContour)
        self.sld_max.valueChanged.connect(self.movedSldMax)
        self.sld_max.sliderReleased.connect(self.imageContour)

        self.sld_dens.valueChanged.connect(self.movedSldDens)
        # self.sld_dens.sliderReleased.connect(self.movedSldDens)
        self.sld_dens.sliderReleased.connect(self.imageDensity)
        self.spb_sld_dens.valueChanged.connect(self.changedSpbSldDens)
        self.spb_sld_dens.valueChanged.connect(self.imageDensity)
        self.spb_sld_min.valueChanged.connect(self.changedSpbSldMin)
        self.spb_sld_max.valueChanged.connect(self.changedSpbSldMax)

        self.sld_paths.valueChanged.connect(self.movedSldPaths)
        self.sld_paths.sliderReleased.connect(self.changedSldPaths)
        self.spb_paths.valueChanged.connect(self.changedSpbSldPaths)
        self.spb_paths.valueChanged.connect(self.changedSldPaths)

        # self.btn_region_init.clicked.connect(self.regionTable)
        # self.btn_region_refresh.clicked.connect(self.regionRefresh)
        # self.btn_region_check.toggled.connect(self.regionCheckMarkerPosition)
        # self.btn_region_export.clicked.connect(self.regionExportPoly)
        #
        self.chbx_mesh_refine.stateChanged.connect(self.changedChbxMeshRefine)
        self.chbx_smooth.stateChanged.connect(self.changedChbxSmooth)
        self.chbx_switches.stateChanged.connect(self.changedChbxSwitches)
        self.chbx_mesh_attr.stateChanged.connect(self.showMesh)
        self.btn_mesh.clicked.connect(self.clickedBtnMesh)
        self.btn_mesh_export.clicked.connect(self.meshExport)
        # menu actions
        self.acn_aboutVerison.triggered.connect(self.aboutVersion)

    def initUI(self):
        # ### icons from https://icons8.com/web-app/category/all/Very-Basic ### #

        style_btn_rs = """
                QPushButton:flat {

                min-height: 30px;
                min-width: 30px;
                }

                QPushButton:hover {
                border: 1px solid #8f8f91;
                border-radius: 3px;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #f6f7fa, stop: 1 #dadbde);
                min-height: 30px;
                min-width: 30px;
                }
            """
        style_btn = """
                QPushButton:flat {

                min-height: 30px;
                min-width: 30px;
                }

                QPushButton:hover {
                border: 1px solid #8f8f91;
                border-radius: 3px;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #f6f7fa, stop: 1 #dadbde);
                min-height: 30px;
                min-width: 30px;
                }
            """
        style_tbx = """
                QToolBox::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #cdcdcd,
                                stop: 0.5 #c4c4c4, stop: 1.0 #bdbaba);
                border-radius: 5px;
                color: #616161;
                }

                QToolBox::tab:selected { /* italicize selected tabs */
                color: black;
                }
            """

        file_widget = QtGui.QWidget()
        self.vbox_file = QtGui.QVBoxLayout()
        self.le_file = QtGui.QLineEdit()
        self.btn_file = QtGui.QPushButton("&File")
        hbox_file = QtGui.QHBoxLayout()
        hbox_file.addWidget(self.btn_file)
        hbox_file.addWidget(self.le_file)
        # small picture of chosen file
        self.file_image = QtGui.QLabel()

        # ## threshold tab of tool_box
        vbox_slds = QtGui.QVBoxLayout()
        self.sld_min = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sld_min.setRange(0, 254)
        self.sld_min.setSliderPosition(200)
        self.spb_sld_min = QtGui.QSpinBox(self)
        self.spb_sld_min.setMinimum(0)
        self.spb_sld_min.setMaximum(254)
        self.spb_sld_min.setValue(200)
        self.sld_max = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sld_max.setRange(1, 255)
        self.sld_max.setSliderPosition(255)
        self.spb_sld_max = QtGui.QSpinBox(self)
        self.spb_sld_max.setMinimum(1)
        self.spb_sld_max.setMaximum(255)
        self.spb_sld_max.setValue(255)
        hbox_min = QtGui.QHBoxLayout()
        hbox_min.addWidget(self.sld_min)
        hbox_min.addWidget(self.spb_sld_min)
        hbox_max = QtGui.QHBoxLayout()
        hbox_max.addWidget(self.sld_max)
        hbox_max.addWidget(self.spb_sld_max)

        vbox_slds.addLayout(hbox_min)
        vbox_slds.addLayout(hbox_max)

        # ## slider for point density
        vbox_sld_dens = QtGui.QVBoxLayout()
        self.sld_dens = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.sld_dens.setRange(1, 20)
        self.sld_dens.setSliderPosition(10)
        self.spb_sld_dens = QtGui.QSpinBox(self)
        self.spb_sld_dens.setMinimum(1)
        self.spb_sld_dens.setMaximum(20)
        self.spb_sld_dens.setValue(10)
        hbox_sld_dens = QtGui.QHBoxLayout()
        hbox_sld_dens.addWidget(self.sld_dens)
        hbox_sld_dens.addWidget(self.spb_sld_dens)
        vbox_sld_dens.addLayout(hbox_sld_dens)
        # vbox_sld_dens.addStretch(1)

        self.sld_paths = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.spb_paths = QtGui.QSpinBox(self)
        hbox_sld_paths = QtGui.QHBoxLayout()
        hbox_sld_paths.addWidget(self.sld_paths)
        hbox_sld_paths.addWidget(self.spb_paths)
        vbox_sld_paths = QtGui.QVBoxLayout()
        vbox_sld_paths.addLayout(hbox_sld_paths)

        le_slds = QtGui.QLabel("Threshold")
        le_sld_dens = QtGui.QLabel("Point density")
        le_sld_paths = QtGui.QLabel("Number of Polys")
        le_dot_opts = QtGui.QLabel("Point Options")
        vbox_slider = QtGui.QVBoxLayout()
        vbox_slider.addWidget(le_slds)
        vbox_slider.addLayout(vbox_slds)
        vbox_slider.addWidget(le_sld_dens)
        vbox_slider.addLayout(vbox_sld_dens)
        vbox_slider.addWidget(le_sld_paths)
        vbox_slider.addLayout(vbox_sld_paths)

        self.vbox_file.addLayout(hbox_file)
        self.vbox_file.addWidget(self.file_image)
        # self.file_image.setGeometry(0, 0, 200, 100)
        self.vbox_file.addLayout(vbox_slider)
        # self.vbox_file.addStretch(1)

        file_widget.setLayout(self.vbox_file)

        # ## scratch tab of tool_box
        scratch_widget = QtGui.QWidget()
        vbox_scratch = QtGui.QVBoxLayout()
        vbox_scratch.addWidget(QtGui.QPlainTextEdit("2 b continued"))
        scratch_widget.setLayout(vbox_scratch)

        # ####################################################################################### #
        #                                    TAB MESH OPTIONS                                     #
        self.la_mesh_quality = QtGui.QLabel("Mesh Quality:")
        self.spb_mesh_quality = QtGui.QDoubleSpinBox(self)
        self.spb_mesh_quality.setMinimum(30.0)
        self.spb_mesh_quality.setMaximum(34.0)
        self.spb_mesh_quality.setValue(30.0)
        self.spb_mesh_quality.setSingleStep(0.1)

        self.la_cell_area = QtGui.QLabel("max. cell area:")
        self.spb_cell_area = QtGui.QDoubleSpinBox(self)
        self.spb_cell_area.setValue(0.0)
        self.spb_cell_area.setSingleStep(0.1)

        self.la_mesh_refine = QtGui.QLabel("Refinement:")
        self.cbx_mesh_refine = QtGui.QComboBox()
        self.cbx_mesh_refine.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.cbx_mesh_refine.setEnabled(False)
        self.chbx_mesh_refine = QtGui.QCheckBox()
        self.cbx_mesh_refine.addItem("quadratic")
        self.cbx_mesh_refine.addItem("spatially")
        self.mesh_refine = False

        self.la_smooth = QtGui.QLabel("Smooth:")
        self.chbx_smooth = QtGui.QCheckBox()
        self.cbx_smooth = QtGui.QComboBox()
        self.cbx_smooth.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.cbx_smooth.setToolTip("1 node center\n2 weighted node center")
        self.cbx_smooth.setEnabled(False)
        # self.cbx_smooth.addItem("0")
        self.cbx_smooth.addItem("1")
        self.cbx_smooth.addItem("2")
        self.spb_smooth = QtGui.QSpinBox()
        self.spb_smooth.setToolTip("number of iterations")
        self.spb_smooth.setEnabled(False)
        self.spb_smooth.setMinimum(1)
        self.spb_smooth.setValue(5)

        self.la_switches = QtGui.QLabel("Switches:")
        self.chbx_switches = QtGui.QCheckBox()
        self.le_switches = QtGui.QLineEdit("-pzeAfaq31")
        self.le_switches.setEnabled(False)
        self.switches = None

        self.la_mesh_show_attr = QtGui.QLabel("Show Attributes:")
        self.chbx_mesh_attr = QtGui.QCheckBox()

        self.btn_mesh = QtGui.QPushButton("mesh")
        self.btn_mesh.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.btn_mesh_export = QtGui.QPushButton()
        self.btn_mesh_export.setToolTip("save as *.bms")
        self.btn_mesh_export.setIcon(QtGui.QIcon("material/ic_save_black_24px.svg"))
        self.btn_mesh_export.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.btn_mesh_export.setEnabled(False)
        # labels stacked in vbox
        vbox_mesh_labels = QtGui.QVBoxLayout()
        vbox_mesh_labels.addWidget(self.la_mesh_quality)
        vbox_mesh_labels.addWidget(self.la_cell_area)
        vbox_mesh_labels.addWidget(self.la_mesh_refine)
        vbox_mesh_labels.addWidget(self.la_smooth)
        vbox_mesh_labels.addWidget(self.la_switches)
        vbox_mesh_labels.addWidget(self.la_mesh_show_attr)
        # rest organized in layout boxes
        vbox_mesh_params = QtGui.QVBoxLayout()
        vbox_mesh_params.addWidget(self.spb_mesh_quality)
        vbox_mesh_params.addWidget(self.spb_cell_area)
        hbox_mesh_refine = QtGui.QHBoxLayout()
        hbox_mesh_refine.addWidget(self.chbx_mesh_refine)
        hbox_mesh_refine.addWidget(self.cbx_mesh_refine)
        vbox_mesh_params.addLayout(hbox_mesh_refine)
        hbox_mesh_smooth = QtGui.QHBoxLayout()
        hbox_mesh_smooth.addWidget(self.chbx_smooth)
        hbox_mesh_smooth.addWidget(self.cbx_smooth)
        hbox_mesh_smooth.addWidget(self.spb_smooth)
        vbox_mesh_params.addLayout(hbox_mesh_smooth)
        # TODO
        # hbox_mesh_switches = QtGui.QHBoxLayout()
        # hbox_mesh_switches.addWidget(self.chbx_switches)
        # hbox_mesh_switches.addWidget(self.le_switches)
        # vbox_mesh_params.addLayout(hbox_mesh_switches)
        hbox_mesh_attr = QtGui.QHBoxLayout()
        hbox_mesh_attr.addWidget(self.chbx_mesh_attr)
        hbox_mesh_attr.addStretch(1)
        vbox_mesh_params.addLayout(hbox_mesh_attr)

        hbox_mesh = QtGui.QHBoxLayout()
        hbox_mesh.addLayout(vbox_mesh_labels)
        hbox_mesh.addLayout(vbox_mesh_params)

        hbox_mesh_n_export = QtGui.QHBoxLayout()
        hbox_mesh_n_export.addWidget(self.btn_mesh)
        hbox_mesh_n_export.addWidget(self.btn_mesh_export)

        vbox_mesh = QtGui.QVBoxLayout()
        vbox_mesh.addLayout(hbox_mesh)
        vbox_mesh.addLayout(hbox_mesh_n_export)
        vbox_mesh.addStretch(1)

        mesh_widget = QtGui.QWidget()
        mesh_widget.setLayout(vbox_mesh)

        # ####################################################################################### #
        #                                      SET UP TOOLBOX                                     #
        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)

        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setIconSize(QtCore.QSize(18, 18))
        self.addToolBar(self.toolBar)

        # initialize the plot widget
        self.plotWidget = PlotWidget(self)
        self.builder = Builder(self)
        self.regions = RegionQuickCheck(self)
        tool_box = QtGui.QTabWidget(self)
        tool_box.setTabPosition(QtGui.QTabWidget.West)
        tool_box.addTab(file_widget, "start with sketch")
        tool_box.addTab(self.builder, "model builder")
        # tool_box.addTab(region_widget, "region manager")
        tool_box.addTab(self.regions, "region manager")
        tool_box.addTab(mesh_widget, "mesh options")
        v_plotWidget = QtGui.QVBoxLayout()
        v_plotWidget.addWidget(self.plotWidget)

        # ### split this
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(tool_box)
        splitter.addWidget(self.plotWidget)

        self.acn_aboutVerison = QtGui.QAction("Version", self)

        menubar = self.menuBar()
        menu_file = menubar.addMenu("&About")
        menu_file.addAction(self.acn_aboutVerison)

        self.setCentralWidget(splitter)

        self.setGeometry(200, 100, 1000, 600)
        # window name
        self.setWindowTitle("GIMod")
        self.show()

    def aboutVersion(self):
        with open('version.json') as v:
            content = v.read()
        QtGui.QMessageBox.information(self, "About", content)

    def movedSldMin(self):
        self.spb_sld_min.setValue(self.sld_min.sliderPosition())
        if self.sld_min.sliderPosition() == self.sld_max.sliderPosition():
            self.sld_max.setSliderPosition(self.sld_max.sliderPosition() + 1)

    def movedSldMax(self):
        self.spb_sld_max.setValue(self.sld_max.sliderPosition())
        if self.sld_max.sliderPosition() == self.sld_min.sliderPosition():
            self.sld_min.setSliderPosition(self.sld_min.sliderPosition() - 1)

    def movedSldDens(self):
        self.spb_sld_dens.setValue(self.sld_dens.sliderPosition())

    def changedSpbSldMin(self):
        self.sld_min.setSliderPosition(self.spb_sld_min.value())

    def changedSpbSldMax(self):
        self.sld_max.setSliderPosition(self.spb_sld_max.value())

    def changedSpbSldDens(self):
        self.sld_dens.setSliderPosition(self.spb_sld_dens.value())

    def changedSpbSldPaths(self):
        self.sld_paths.setSliderPosition(self.spb_paths.value())

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

    def chooseOpenSketch(self):
        # introduce the safe option for points here, because this function is
        # called once per sketch
        self.x_safe = []
        self.y_safe = []
        self.fname = QtGui.QFileDialog.getOpenFileName(
            self, caption="choose sketch")
        if self.fname:
            self.le_file.setText(self.fname)
            pixmap = QtGui.QPixmap(self.fname)
            myScaledPixmap = pixmap.scaled(self.file_image.size(), QtCore.Qt.KeepAspectRatio)
            self.vbox_file.addStretch(1)
            self.file_image.setPixmap(myScaledPixmap)
            # self.file_image.setFrameShape(QtGui.QFrame.StyledPanel)
            # self.file_image.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
            self.vbox_file.addStretch(1)

            self.imageContour()

    def imageContour(self):
        # Read image
        src = cv2.imread(self.fname)
        img = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        # self.x_range, self.y_range = img.shape

        # Basic threshold example
        th, dst = cv2.threshold(img, float(self.sld_min.sliderPosition()), float(
            self.sld_max.sliderPosition()), cv2.THRESH_BINARY)

        # Find Contours
        image, contours, hierarchy = cv2.findContours(
            dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # sort after polygon area and takes the 10 biggest
        paths = sorted(contours, key=cv2.contourArea)[::-1]  # [-11:-1]
        self.paths = [i for i in paths if len(i) > 5][1:]
        if len(self.paths) >= 50:
            self.statusBar.showMessage("WARNING: detected %i polygons... possible bad conditioned threshold or image" % (len(self.paths)))
        else:
            self.statusBar.clearMessage()
        self.sld_paths.setRange(1, len(self.paths))
        self.sld_paths.setSliderPosition(1)
        self.spb_paths.setMinimum(1)
        self.spb_paths.setMaximum(len(self.paths))
        self.spb_paths.setValue(1)
        # draw initially
        self.changedSldPaths()
        # print(len(self.paths))
        # print(len(paths[-11:-1]))
        # sys.exit()

    def movedSldPaths(self):
        self.spb_paths.setValue(self.sld_paths.sliderPosition())

    def changedSldPaths(self):
        self.paths_cut = self.paths[:self.spb_paths.value()]
        self.polygons = []
        for path in self.paths_cut:
            tuples = []
            for tup in path:
                tuples.append([float(tup[0][0]), float(tup[0][1])])
            self.polygons.append(tuples)

        self.imageDensity()
        # TODO achse auf 0 - 1 begrenzen und skala selbst angeben können

    def findMinMax(self):
        """
            # TODO: force deprecation!!!!
            nur gebraucht bei createWorld in regionRefresh
        """
        min_x = []
        max_x = []
        min_y = []
        max_y = []
        for p in self.polygons:
            min_x.append(min(p, key=lambda t: t[0])[0])
            max_x.append(max(p, key=lambda t: t[0])[0])
            min_y.append(min(p, key=lambda t: t[1])[1])
            max_y.append(max(p, key=lambda t: t[1])[1])

        self.min_x = min(min_x)
        self.max_x = max(max_x)
        self.min_y = min(min_y)
        self.max_y = max(max_y)

    def imageDensity(self):
        """ take every n-th tuple given from the slider 'density' to reduce number of points """
        self.polygons_dens = []
        for p in self.polygons:
            self.polygons_dens.append([p[i] for i in range(0, len(p), self.spb_sld_dens.value())])
        self.findMinMax()
        self.imagePlot()

    def imagePlot(self):
        self.plotWidget.axis.cla()
        for p in self.polygons_dens:
            # print(path)
            # print(path.shape)
            self.plotWidget.axis.scatter(*zip(*p), alpha=0.5, s=2)

        self.plotWidget.canvas.draw()
        # self.btn_region_init.setEnabled(True)
        # self.rbtn_region_regions.setEnabled(True)
        # self.rbtn_region_attributes.setEnabled(True)

        # if self.btn_rs.isChecked() is False and len(self.x) != 0:
        #     self.btn_mesh.setEnabled(True)

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
            self.smooth_method = [int(self.cbx_smooth.currentText()), self.spb_smooth.value()]

        if self.chbx_switches.isChecked() is False:
            self.switches = None
        else:
            self.switches = self.le_switches.text()
            # TODO make th switches work --> http://pygimli.org/_examples_auto/modelling/plot_hybrid-mesh-2d.html?highlight=switches

        self.statusBar.showMessage("generating mesh...")
        self.mesh = createMesh(self.regions.getPoly(), quality=self.spb_mesh_quality.value(), area=self.spb_cell_area.value(), smooth=self.smooth_method, switches=self.switches)

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
            pg.show(drawMeshBoundaries(self.plotWidget.axis, self.mesh, hideMesh=False), ax=self.plotWidget.axis, fillRegion=False)
        else:
            pg.show(self.mesh, ax=self.plotWidget.axis)

        self.plotWidget.axis.set_ylim(self.plotWidget.axis.get_ylim()[::-1])
        self.plotWidget.canvas.draw()

    def meshExport(self):
        """
            export the final mesh
        """
        export_mesh = QtGui.QFileDialog.getSaveFileName(
            self, caption="Save Mesh")

        # if export_poly:
        if export_mesh.endswith(".bms"):
            writePLC(self.mesh, export_mesh)
        else:
            writePLC(self.mesh, export_mesh + ".bms")


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("MainWindow")

    main = MainWindow()
    # main.resize(600, 600)
    main.show()

    sys.exit(app.exec_())
