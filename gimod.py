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


class PlotWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)

        # a figure instance to plot on
        self.figure = Figure()
        self.figure.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.95, hspace=0.4, wspace=0.1)
        self.axis = self.figure.add_subplot(111)

        self.axis.set_xlabel("x")
        self.axis.set_ylabel("z")
        self.axis.set_ylim(self.axis.get_ylim()[::-1])
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        # layout.addWidget(self.button)
        self.setLayout(layout)


class DraggablePoint(object):
    """
    thank you very much:
    http://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively
    """
    lock = None  # only one can be animated at a time

    def __init__(self, point=None, marker=None, center=None):
        # print("dp init")
        self.point = point
        self.press = None
        self.background = None
        self.center = center
        self.marker = marker
        self.params = (self.marker, self.center)
        self.dict = {}
        # FIXME: WTF!!!! die initialisierung SCHEINT hier notwendig, da die funktionen on_press/release/motion andernfalls nicht aufgerufen werden. WARUM AUCH IMMER. unnötig bei python 3.4.3 und mpl 1.4.3 @nico
        self.on_press = self.on_press

    def connect(self):
        """
            connect to all the events we need
        """
        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        # if press out ouf point boundary
        if event.inaxes != self.point.axes:
            return
        # if more than one object oculd be moved
        if DraggablePoint.lock is not None:
            return
        contains, attrd = self.point.contains(event)
        if not contains:
            return
        self.press = (self.point.center), event.xdata, event.ydata
        DraggablePoint.lock = self
        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.point.figure.canvas
        axes = self.point.axes
        self.point.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.point.axes.bbox)
        # now redraw just the rectangle
        axes.draw_artist(self.point)
        # and blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_motion(self, event):
        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.point.axes:
            return
        self.point.center, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.point.center = (self.point.center[0]+dx, self.point.center[1]+dy)

        canvas = self.point.figure.canvas
        axes = self.point.axes
        # restore the background region
        canvas.restore_region(self.background)
        # redraw just the current rectangle
        axes.draw_artist(self.point)
        # blit just the redrawn area
        canvas.blit(axes.bbox)

    def on_release(self, event):
        """
            on release we reset the press data
        """
        if DraggablePoint.lock is not self:
            return
        self.press = None
        DraggablePoint.lock = None
        # turn off the rect animation property and reset the background
        self.point.set_animated(False)
        self.background = None
        # redraw the full figure
        self.point.figure.canvas.draw()
        self.center = event.xdata, event.ydata
        # return self.marker, self.center
        self.returnValue()

    def returnValue(self):
        """
            added by myself to get the final marker position after movement out of the class objects
        """
        self.dict[self.marker] = self.point.center
        return self.dict

    def disconnect(self):
        """
            disconnect all the stored connection ids
        """
        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)


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

        # self.btn_rs.clicked.connect(self.triggeredRectangleSelection)
        # self.btn_del.clicked.connect(self.imageDeleteSelected)
        # self.btn_undo.clicked.connect(self.clickedImageDeleteUndo)
        #
        self.btn_region_init.clicked.connect(self.regionTable)
        self.btn_region_refresh.clicked.connect(self.regionRefresh)
        # self.chbx_region_check.stateChanged.connect(self.regionCheckMarkerPosition)
        # self.chbx_region_check_finished.stateChanged.connect(self.regionMoveMarkersFinished)
        # self.rbtn_region_regions.stateChanged.connect(self.toggledRegionCheckBoxes)
        # self.rbtn_region_attributes.stateChanged.connect(self.toggledRegionCheckBoxes)
        self.btn_region_check.toggled.connect(self.regionCheckMarkerPosition)
        self.btn_region_export.clicked.connect(self.regionExportPoly)
        #
        self.chbx_mesh_refine.stateChanged.connect(self.changedChbxMeshRefine)
        self.chbx_smooth.stateChanged.connect(self.changedChbxSmooth)
        self.chbx_switches.stateChanged.connect(self.changedChbxSwitches)
        self.chbx_mesh_attr.stateChanged.connect(self.showMesh)
        self.btn_mesh.clicked.connect(self.clickedBtnMesh)
        self.btn_mesh_export.clicked.connect(self.meshExport)

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
        #
        # # ## menu bar
        # openfile_action = QtGui.QAction("&Open Sketch", self)
        # openfile_action.setShortcut("Ctrl+O")
        # openfile_action.setStatusTip("load sketch to use as model")
        # openfile_action.triggered.connect(self.chooseOpenSketch)
        # exit_action = QtGui.QAction("&Exit", self)
        # exit_action.setShortcut("Ctrl+Q")
        # exit_action.triggered.connect(self.close)
        # exit_action.setStatusTip("exit application")
        #
        # # self.statusBar = QtGui.QStatusBar()
        # menubar = self.menuBar()
        # # '&' makes short key accessible via 'alt + f'
        # fileMenu = menubar.addMenu("&File")
        # fileMenu.addAction(openfile_action)
        # fileMenu.addSeparator()
        # fileMenu.addAction(exit_action)

        # ## first tab of tool_box
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

        # # ## rectangle selection button
        # self.btn_rs = QtGui.QPushButton(self)
        # self.btn_rs.setToolTip("activate point selection")
        # self.btn_rs.setCheckable(True)
        # self.btn_rs.setStyleSheet(style_btn_rs)
        # self.btn_rs.setIcon(QtGui.QIcon("icons2/External-Link.svg"))
        # # self.btn_rs.setIconSize(QtCore.QSize(30, 30))
        # self.btn_del = QtGui.QPushButton(self)
        # self.btn_del.setToolTip("delete selected points")
        # self.btn_del.setIcon(
        #     self.style().standardIcon(QtGui.QStyle.SP_TrashIcon))
        # # self.btn_del.setIconSize(QtCore.QSize(30, 30))
        # self.btn_del.setEnabled(False)
        # self.btn_del.setStyleSheet(style_btn)
        # self.btn_undo = QtGui.QPushButton(self)
        # # self.btn_undo.setIcon(QtGui.QIcon("icons2/Delete.svg"))
        # # self.btn_undo.setIcon(QtGui.QIcon.fromTheme(QtCore.QString.fromUtf8("document-open")))
        # self.btn_undo.setIcon(
        #         self.style().standardIcon(QtGui.QStyle.SP_ArrowBack))
        # self.btn_undo.setToolTip("undo deletions")
        # # self.btn_undo.setIconSize(QtCore.QSize(30, 30))
        # self.btn_undo.setEnabled(False)
        # self.btn_undo.setStyleSheet(style_btn)
        # hbox_dot_options = QtGui.QHBoxLayout()
        # hbox_dot_options.addWidget(self.btn_rs)
        # hbox_dot_options.addWidget(self.btn_del)
        # hbox_dot_options.addWidget(self.btn_undo)

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
        # vbox_slider.addWidget(le_dot_opts)
        # vbox_slider.addLayout(hbox_dot_options)
        # grp_dot_options = QtGui.QGroupBox("dot options")
        # grp_dot_options.setLayout(hbox_dot_options)
        # slider_widget = QtGui.QWidget()
        # slider_widget.setLayout(vbox_slider)

        self.vbox_file.addLayout(hbox_file)
        self.vbox_file.addWidget(self.file_image)
        #self.file_image.setGeometry(0, 0, 200, 100)
        self.vbox_file.addLayout(vbox_slider)
        # self.vbox_file.addStretch(1)

        file_widget.setLayout(self.vbox_file)
        # ## END first tab of tool_box

        # hbox_btns = QtGui.QHBoxLayout()
        # self.btn1 = QtGui.QPushButton("Polygone mergen?", self)
        # self.btn2 = QtGui.QPushButton("Punkte löschen?", self)
        # self.btn3 = QtGui.QPushButton("3", self)
        # hbox_btns.addWidget(self.btn1)
        # hbox_btns.addWidget(self.btn2)
        # hbox_btns.addWidget(self.btn3)

        # ## scratch tab of tool_box
        scratch_widget = QtGui.QWidget()
        vbox_scratch = QtGui.QVBoxLayout()
        vbox_scratch.addWidget(QtGui.QPlainTextEdit("2 b continued"))
        scratch_widget.setLayout(vbox_scratch)

        # ####################################################################################### #
        #                                   TAB REGION MANAGER                                    #
        self.btn_region_init = QtGui.QPushButton("initialize")

        # attribute table of the model
        self.region_table = QtGui.QTableWidget(self)
        self.region_table.setColumnCount(3)
        self.region_table.setHorizontalHeaderLabels(("Marker #", "Hole?", "Attribute"))

        # button refresh to plot the model again after configurations in the table have been made
        self.btn_region_refresh = QtGui.QPushButton("refresh")
        self.btn_region_refresh.setEnabled(False)

        # plotting options... regions
        self.rbtn_region_regions = QtGui.QRadioButton("plot regions")
        self.rbtn_region_regions.setChecked(True)
        # plotting options... attributes
        self.rbtn_region_attributes = QtGui.QRadioButton("plot attributes")
        # checkbox to open dialog for moving the marker points
        # self.chbx_region_check = QtGui.QCheckBox("correct marker positions")
        # self.chbx_region_check.setEnabled(False)
        # self.chbx_region_check_finished = QtGui.QCheckBox("finished")
        # hbox_region_check = QtGui.QHBoxLayout()
        # hbox_region_check.addWidget(self.chbx_region_check)
        # hbox_region_check.addWidget(self.chbx_region_check_finished)

        # check regions
        self.btn_region_check = QtGui.QPushButton("check region markers")
        self.btn_region_check.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.btn_region_check.setCheckable(True)
        self.btn_region_check.setEnabled(False)
        self.btn_region_export = QtGui.QPushButton()
        self.btn_region_export.setToolTip("save as *.poly")
        self.btn_region_export.setIcon(QtGui.QIcon("icons/Devices-volumes-Floppy.svg"))
        self.btn_region_export.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        # self.btn_region_export.setIconSize(QtCore.QSize(30, 30))
        self.btn_region_export.setEnabled(False)

        hbox_1 = QtGui.QHBoxLayout()
        hbox_1.addWidget(self.rbtn_region_regions)
        hbox_1.addWidget(self.btn_region_refresh)
        hbox_2 = QtGui.QHBoxLayout()
        hbox_2.addWidget(self.rbtn_region_attributes)
        hbox_2.addStretch(1)
        hbox_3 = QtGui.QHBoxLayout()
        hbox_3.addWidget(self.btn_region_check)
        hbox_3.addWidget(self.btn_region_export)

        vbox_region2 = QtGui.QVBoxLayout()
        vbox_region2.addWidget(self.btn_region_init)
        # vbox_region2.addLayout(vbox_region1)
        vbox_region2.addLayout(hbox_1)
        vbox_region2.addLayout(hbox_2)
        vbox_region2.addWidget(self.region_table)
        vbox_region2.addLayout(hbox_3)

        region_widget = QtGui.QWidget()
        region_widget.setLayout(vbox_region2)

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
        self.btn_mesh_export.setIcon(QtGui.QIcon("icons/Devices-volumes-Floppy.svg"))
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
        tool_box = QtGui.QToolBox()
        tool_box.addItem(file_widget, "start with sketch")
        # tool_box.addItem(scratch_widget, "start from scratch")
        tool_box.addItem(region_widget, "region manager")
        tool_box.addItem(mesh_widget, "mesh options")
        tool_box.setStyleSheet(style_tbx)
        # make the toolbox frame ready... since this needs a QLayout
        v_tool_box = QtGui.QVBoxLayout()
        v_tool_box.addWidget(tool_box)

        # tabBar = QtGui.QTabBar()
        # tabBar.addTab("Threshold")
        # hbox_grps = QtGui.QHBoxLayout()
        # hbox_grps.addWidget(groupbox_slds)
        # hbox_grps.addWidget(groupbox_sld_dens)
        # initialize the plot widget
        self.plotWidget = PlotWidget(self)
        # self.plotWidget.setStatusTip("model area")
        v_plotWidget = QtGui.QVBoxLayout()
        v_plotWidget.addWidget(self.plotWidget)

        # ### initiate frames
        frame_left = QtGui.QFrame()
        frame_left.setFrameShape(QtGui.QFrame.StyledPanel)
        frame_left.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        # frame_left.setStyleSheet("background-color: lightgray")
        frame_right = QtGui.QFrame()
        frame_right.setFrameShape(QtGui.QFrame.StyledPanel)
        frame_right.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)

        # ### add content
        frame_left.setLayout(v_tool_box)
        frame_right.setLayout(v_plotWidget)

        # ### split this
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(frame_left)
        splitter.addWidget(frame_right)

        self.statusBar = QtGui.QStatusBar()
        self.setStatusBar(self.statusBar)
        # self.statusBar()
        # ## vbox_widget
        # vbox_central = QtGui.QVBoxLayout()
        # vbox_central.addWidget(splitter)
        # vbox_central.addWidget(self.statusBar)
        # # von hinten durch die brust ins auge
        # central_widget = QtGui.QWidget()
        # central_widget.setLayout(vbox_central)
        # groupbox_central = QtGui.QGroupBox()
        # groupbox_central.setLayout(vbox_central)

        self.setCentralWidget(splitter)
        # self.setCentralWidget(central_widget)

        self.setGeometry(100, 100, 1000, 600)
        # window name
        self.setWindowTitle("GIMod")
        self.show()

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
        # self.x_dens = [self.x[i]
        #           for i in range(0, len(self.x), self.spb_sld_dens.value())]
        # self.y_dens = [self.y[i]
        #           for i in range(0, len(self.y), self.spb_sld_dens.value())]
        self.polygons_dens = []
        for p in self.polygons:
            self.polygons_dens.append([p[i] for i in range(0, len(p), self.spb_sld_dens.value())])
        self.findMinMax()
        self.imagePlot()

    def imagePlot(self):
        self.plotWidget.axis.cla()
        # self.plotWidget.axis.set_xlim(self.min_x - 50, self.max_x + 50)
        # self.plotWidget.axis.set_ylim(self.max_y + 50, self.min_y - 50)
        # self.plotWidget.axis.set_aspect("equal")
        # self.plotWidget.axis.scatter(self.x_dens, self.y_dens, alpha=0.5, s=2)
        for p in self.polygons_dens:
            # print(path)
            # print(path.shape)
            self.plotWidget.axis.scatter(*zip(*p), alpha=0.5, s=2)

        self.plotWidget.canvas.draw()

        # if self.btn_rs.isChecked() is False and len(self.x) != 0:
        #     self.btn_mesh.setEnabled(True)

    def imagePlotSelected(self):
        # self.x_del = np.empty(1, dtype=int)
        # self.y_del = np.empty(1, dtype=int)
        x_ = np.where((self.x_dens >= self.x1) & (self.x_dens <= self.x2))[0]
        y_ = np.where((self.y_dens >= self.y1) & (self.y_dens <= self.y2))[0]
        self.common = np.intersect1d(x_, y_)

        self.x_del = [self.x_dens[i] for i in self.common]
        self.y_del = [self.y_dens[i] for i in self.common]

        if len(self.x_del) == 0 and len(self.y_del) == 0:
            self.imagePlot()
        else:
            self.plotWidget.axis.scatter(
                self.x_del, self.y_del, s=10, c="red", edgecolor="none")
            self.plotWidget.canvas.draw()

    def imageDeleteSelected(self):
        if len(self.x_del) != 0 and len(self.y_del) != 0:
            # construct new x, y arrays so deleting is reversible
            self.x_dens = np.delete(self.x_dens, self.common).tolist()
            self.y_dens = np.delete(self.y_dens, self.common).tolist()
            # save them for possible undoing and reverse so the last change is the first to undo
            # safer packing [] so the array will be contained even if its only
            # one
            self.x_safe.append(self.x_del)
            self.y_safe.append(self.y_del)
            # empty the deletion lists so nothing weird happens...
            self.x_del = []
            self.y_del = []
            self.imagePlot()

    # def clickedImageDeleteUndo(self):
    #     try:
    #         self.x_dens = self.x_dens + self.x_safe[-1]
    #         self.y_dens = self.y_dens + self.y_safe[-1]
    #         # since it will be plottet again, there is no need to save it.. so
    #         # delete
    #         del self.x_safe[-1]
    #         del self.y_safe[-1]
    #
    #         self.imagePlot()
    #     except IndexError:
    #         # self.statusBar.showMessage("nothing to undo")
    #         pass

    # def rectSelectCallback(self, eclick, erelease):
    #     'eclick and erelease are the press and release events'
    #     # ## sort x and y
    #     self.x1, self.x2 = min(eclick.xdata, erelease.xdata), max(
    #         eclick.xdata, erelease.xdata)
    #     self.y1, self.y2 = min(eclick.ydata, erelease.ydata), max(
    #         eclick.ydata, erelease.ydata)
    #     self.imagePlotSelected()
    #
    # def toggleSelector(self, event):
    #     # print(' Key pressed.')
    #     if event.key in ['Q', 'q'] and self.toggleSelector.active:
    #         # print(' RectangleSelector deactivated.')
    #         self.toggleSelector.set_active(False)
    #     if event.key in ['A', 'a'] and not self.toggleSelector.active:
    #         # print(' RectangleSelector activated.')
    #         self.toggleSelector.set_active(True)

    # def triggeredRectangleSelection(self):
    #     if self.btn_rs.isChecked() is True:
    #         self.btn_del.setEnabled(True)
    #         self.btn_undo.setEnabled(True)
    #
    #         self.toggleSelector = RectangleSelector(self.plotWidget.axis,
    #                                                  self.rectSelectCallback,
    #                                                  drawtype='box', useblit=True,
    #                                                  # only use left click
    #                                                  button=[1],
    #                                                  minspanx=5, minspany=5,
    #                                                  spancoords='pixels',
    #                                                  interactive=False)
    #         self.plotWidget.canvas.draw()
    #
    #     else:
    #         self.toggleSelector.set_active(False)
    #         self.btn_del.setEnabled(False)
    #         self.btn_undo.setEnabled(False)

    # def toggledRegionCheckBoxes(self):
    #     """ just turn off the other """
    #     if self.rbtn_region_attributes.isChecked() is True:
    #         self.rbtn_region_regions.setChecked(False)
    #     elif self.rbtn_region_regions.isChecked() is True:
    #         self.rbtn_region_attributes.setChecked(False)

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
        self.mesh = createMesh(self.poly, quality=self.spb_mesh_quality.value(), area=self.spb_cell_area.value(), smooth=self.smooth_method, switches=self.switches)

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

    """ ###############                      REGION MANAGER                      ############### """
    def regionRefresh(self, new_markers=False):
        """
        detect polygons, mark them im order and plot result
        """
        # store the marker positions to check if they are in their respective polygon
        self.marker_positions = []
        # create world where model is placed with a certain distance to the border
        # TODO maybe add option to set the distance to border
        self.poly = plc.createWorld(start=[self.min_x - 100, self.max_y + 100], end=[self.max_x + 100, self.min_y - 100], marker=1)

        # print(type(self.region_table.cellWidget(0, 1).currentText()))
        for i, p in enumerate(self.polygons_dens):
            poly = plc.createPolygon(p, isClosed=True)
            if new_markers:
                marker_pos = new_markers[i][0]
            else:
                marker_pos = self.regionCentroid(p)

            # check if polygon is not hole
            if self.region_table.cellWidget(i+1, 1).currentText() == "False":
                pg.Mesh.addRegionMarker(poly, marker_pos, marker=int(self.region_table.cellWidget(i+1, 0).currentText()))
            # or else
            else:
                pg.Mesh.addHoleMarker(poly, marker_pos)

            self.poly = plc.mergePLC([self.poly, poly])
            self.marker_positions.append(marker_pos)

        self.statusBar.showMessage(str(self.poly))
        self.regionShow()

    def regionCentroid(self, poly):
        """
            find centroid as marker position
            # TODO
            ...potentially dangerous method... since the center could be overlayed by another polygon
        """
        ref_polygon = Polygon(poly)
        # get the x and y coordinate of the centroid
        pnts = ref_polygon.centroid.wkt.split(" ")[1:]

        return (float(pnts[0][1:]), float(pnts[1][:-1]))

    def regionShow(self):
        """
            plot regions (or attribute table)
        """
        self.plotWidget.axis.cla()
        if self.rbtn_region_regions.isChecked() is True:
            drawPLC(self.plotWidget.axis, self.poly)

        elif self.rbtn_region_attributes.isChecked() is True:
            self.regionGetAttributes()
            mesh_tmp = createMesh(self.poly)
            try:
                attr_map = pg.solver.parseMapToCellArray(self.attr_map, mesh_tmp)
                drawMeshBoundaries(self.plotWidget.axis, mesh_tmp, hideMesh=True)
                drawModel(self.plotWidget.axis, mesh_tmp, tri=True, alpha=0.65, data=attr_map)

            except (AttributeError, IndexError):
                # self.statusBar.showMessage("unsufficient data in attribute table")
                self.statusBar.showMessage("ERROR: wrong or missing values in attribute table")
                pass

        self.plotWidget.axis.set_ylim(self.plotWidget.axis.get_ylim()[::-1])
        self.plotWidget.canvas.draw()


    def regionTable(self):
        """
            - overview the regions of the model
            - see marker and assign attributes
        """
        # self.region_table.clear()
        self.region_table.setRowCount(len(self.polygons_dens) + 1)  # +1 for world around model

        # TODO an die marker direkt rankommen.. wie viele sinds.. denn so lange bleibts ein
        # HACK:
        for i in range(len(self.polygons_dens) + 1):  # row
            # column 1 - region marker no.
            cbx_marker = QtGui.QComboBox(self.region_table)
            [cbx_marker.addItem(str(m+1)) for m in range(len(self.polygons_dens) + 1)]
            cbx_marker.setCurrentIndex(i)
            self.region_table.setCellWidget(i, 0, cbx_marker)

            # column 2 - isHoleMarker
            cbx_isHole = QtGui.QComboBox(self.region_table)
            cbx_isHole.addItem("False")
            cbx_isHole.addItem("True")
            self.region_table.setCellWidget(i, 1, cbx_isHole)

            # column 3 - attributes
            self.region_table.setItem(i, 2, QtGui.QTableWidgetItem("None"))

        self.region_table.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.region_table.resizeColumnsToContents()

        # allow new options now since the poly exists now
        self.btn_region_refresh.setEnabled(True)
        self.btn_region_check.setEnabled(True)
        self.btn_region_export.setEnabled(True)
        # self.chbx_region_check.setEnabled(True)
        self.regionRefresh()

    def regionGetAttributes(self):
        """
            before going on with plotting the attributes etc. check for nonsense and multiple value
            specifications for the one marker
        """
        key_attr = False
        self.attr_map = []
        tmp_mark = []
        tmp_attr = []
        tmp_idx = []
        for i in range(len(self.polygons_dens) + 1):
            try:
                # get values from attribute column
                mark = int(self.region_table.cellWidget(i, 0).currentText())
                attr = float(self.region_table.item(i, 2).text())
                if mark not in tmp_mark:
                    tmp_mark.append(mark)
                else:
                    tmp_idx.append(i)
                    tmp_attr.append(attr)
                self.attr_map.append([mark, attr])
                if self.region_table.cellWidget(i, 1).currentText() == "False":
                    # fill green if successfull
                    self.region_table.item(i, 2).setBackground(QtGui.QColor(2, 164, 6, 0.5 * 255))
                else:
                    # or white if its hole and it doesnt matter
                    self.region_table.item(i, 2).setBackground(QtGui.QColor(255, 255, 255, 0.5 * 255))
            except ValueError:
                if self.region_table.cellWidget(i, 1).currentText() == "False":
                    # fill red if error
                    self.region_table.item(i, 2).setBackground(QtGui.QColor(172, 7, 0, 0.5 * 255))
                    key_attr = True
                else:
                    # or white if its hole and it doesnt matter
                    self.region_table.item(i, 2).setBackground(QtGui.QColor(255, 255, 255, 0.5 * 255))
        # check if duplicates in attribute column exists. len 0 means different  values for same
        # marker
        if len([k for k, v in Counter(tmp_attr).items() if v>1]) == 0:
            for idx in tmp_idx:
                self.region_table.item(idx, 2).setBackground(QtGui.QColor(255, 179, 0, 0.5 * 255))
                key_attr = True

        if key_attr:
            self.statusBar.showMessage("WARNING: duplicate or wrong data in attribute table")

    def regionCheckMarkerPosition(self):
        """
            check if every marker position is in its respective polygon. the distance between
            marker position and polygon border should be shortest if its the own polygon!
        """
        warning = False
        if self.btn_region_check.isChecked() is True:
            for i, mark in enumerate(self.marker_positions):
                point = Point(mark)
                for k, poly in enumerate(self.polygons_dens):
                    dist = point.distance(Polygon(poly))
                    # print(i+2, k+2, dist)
                    if i != k and dist == 0.:
                        warning = True

            if warning:
                self.statusBar.showMessage("WARNING: possible multiple markers in a polygon... continue at own risk")
                self.regionMoveMarkers()
            else:
                self.statusBar.showMessage("regions and markers seem to be fine", 3000)

        else:
            new_markers = []
            for p in self.dps:
                val = p.returnValue()
                new_markers.append(list(val.values()))
                p.disconnect()
            self.statusBar.showMessage("updating...")

            self.regionRefresh(new_markers=new_markers)

    def regionMoveMarkers(self):
        """
            plots dots as marker positions which can be moved
        """
        self.dps = []

        for i, m in enumerate(self.marker_positions):
            mark = patches.Circle(m, radius=8, fc="r")
            self.plotWidget.axis.add_patch(mark)
            dp = DraggablePoint(mark, i+2, m)
            dp.connect()
            self.dps.append(dp)
        self.plotWidget.canvas.draw()

    def regionExportPoly(self):
        """
            export the poly figure
        """
        export_poly = QtGui.QFileDialog.getSaveFileName(
            self, caption="Save Poly Figure")

        # if export_poly:
        if export_poly.endswith(".poly"):
            writePLC(self.poly, export_poly)
        else:
            writePLC(self.poly, export_poly + ".poly")


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("MainWindow")

    main = MainWindow()
    # main.resize(600, 600)
    main.show()

    sys.exit(app.exec_())
