# TODO: current state of development... needs to be sorted out
try:
    from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QLineEdit,  QPushButton, QStatusBar, QToolBar, QTabWidget, QSplitter, QAction, QMessageBox
    from PyQt5.QtCore import QSize, Qt
    from PyQt5.QtGui import QIcon

except ImportError:
    from PyQt4.QtGui import QMainWindow, QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QLineEdit,  QPushButton, QStatusBar, QToolBar, QTabWidget, QSplitter, QAction, QMessageBox, QIcon
    from PyQt4.QtCore import QSize, Qt

from pygimli import show
from pygimli.meshtools import createMesh, writePLC
from pygimli.mplviewer import drawMeshBoundaries, drawMesh, drawPLC, drawModel


class MeshOptions(QWidget):
    """Graphical access to the options for meshing a poly file."""

    def __init__(self, parent=None):
        """
        Initialize the main functionality.

        Parameters
        ----------
        parent: <__main__.GIMod object>
            The elder parent class
        """
        # call the super class to establish the functionality of a QWidget
        super(MeshOptions, self).__init__(parent)
        self.parent = parent
        self.setupWidget()

        # connect the signals to theri functions
        self.chbx_mesh_refine.stateChanged.connect(self.changedChbxMeshRefine)
        self.chbx_smooth.stateChanged.connect(self.changedChbxSmooth)
        self.chbx_switches.stateChanged.connect(self.changedChbxSwitches)
        self.chbx_mesh_attr.stateChanged.connect(self.showMesh)
        self.btn_mesh.clicked.connect(self.clickedBtnMesh)
        self.btn_mesh_export.clicked.connect(self.meshExport)

    def setupWidget(self):
        """Design the layout of the tab that holds the options for tetgen."""
        # define the mesh quality regarding the inner angle in a cell
        la_mesh_quality = QLabel("Mesh Quality:")
        self.spb_mesh_quality = QDoubleSpinBox(self)
        self.spb_mesh_quality.setMinimum(30.0)
        self.spb_mesh_quality.setMaximum(34.0)
        self.spb_mesh_quality.setValue(30.0)
        self.spb_mesh_quality.setSingleStep(0.1)

        # define the maximum area a cell can adjust to
        la_cell_area = QLabel("max. cell area:")
        self.spb_cell_area = QDoubleSpinBox(self)
        self.spb_cell_area.setValue(0.0)
        self.spb_cell_area.setSingleStep(0.01)

        # define the box to choose which refinement algorithm might be chosen
        la_mesh_refine = QLabel("Refinement:")
        self.cbx_mesh_refine = QComboBox()
        self.cbx_mesh_refine.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cbx_mesh_refine.setEnabled(False)
        self.chbx_mesh_refine = QCheckBox()
        self.cbx_mesh_refine.addItem("quadratic")
        self.cbx_mesh_refine.addItem("spatially")
        # REVIEW: whats this?!
        self.mesh_refine = False

        # define the smoothness variable and the number of iterations
        la_smooth = QLabel("Smooth:")
        self.chbx_smooth = QCheckBox()
        self.cbx_smooth = QComboBox()
        self.cbx_smooth.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cbx_smooth.setToolTip("1 node center\n2 weighted node center")
        self.cbx_smooth.setEnabled(False)
        # TODO: replace 1 and 2 with the thing they're representing, sending the algorithm by number later on
        self.cbx_smooth.addItem("1")
        self.cbx_smooth.addItem("2")
        self.spb_smooth = QSpinBox()
        self.spb_smooth.setToolTip("number of iterations")
        self.spb_smooth.setEnabled(False)
        self.spb_smooth.setMinimum(1)
        self.spb_smooth.setValue(5)

        # define the set of switches to override the other adjustments and
        # access tetgen directly through the commandline options
        self.la_switches = QLabel("Switches:")
        self.chbx_switches = QCheckBox()
        self.le_switches = QLineEdit("-pzeAfaq31")
        self.le_switches.setEnabled(False)
        self.switches = None

        # allow colored attribute table overlay together with the mesh
        la_mesh_show_attr = QLabel("Show Attributes:")
        self.chbx_mesh_attr = QCheckBox()

        # the button to hit and run
        self.btn_mesh = QPushButton("mesh")
        self.btn_mesh.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        # define a button to export the just generated mesh
        self.btn_mesh_export = QPushButton()
        self.btn_mesh_export.setToolTip("save as *.bms")
        self.btn_mesh_export.setIcon(QIcon("icons/ic_save_black_24px.svg"))
        self.btn_mesh_export.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.btn_mesh_export.setEnabled(False)

        # stack the labels in a vertical layout
        vbox_mesh_labels = QVBoxLayout()
        vbox_mesh_labels.addWidget(la_mesh_quality)
        vbox_mesh_labels.addWidget(la_cell_area)
        vbox_mesh_labels.addWidget(la_mesh_refine)
        vbox_mesh_labels.addWidget(la_smooth)
        vbox_mesh_labels.addWidget(self.la_switches)
        vbox_mesh_labels.addWidget(la_mesh_show_attr)

        # stack the widgets also vertical so it looks nice and clean
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

        # TODO: make the label auto adjusted to the changes from the widgets
        # TODO:disable all widgets if one wants to set the options by hand
        hbox_mesh_switches = QHBoxLayout()
        hbox_mesh_switches.addWidget(self.chbx_switches)
        hbox_mesh_switches.addWidget(self.le_switches)
        vbox_mesh_params.addLayout(hbox_mesh_switches)

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

        self.setLayout(vbox_mesh)

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

        self.parent.statusBar.showMessage("generating mesh...")
        self.mesh = createMesh(self.parent.builder.getPoly(), quality=self.spb_mesh_quality.value(
        ), area=self.spb_cell_area.value(), smooth=self.smooth_method, switches=self.switches)

        if self.mesh_refine is True and self.cbx_mesh_refine.currentText() == "quadratic":
            self.parent.statusBar.showMessage("create quadratic...")
            self.mesh = self.mesh.createP2()
        elif self.mesh_refine is True and self.cbx_mesh_refine.currentText() == "spatially":
            self.parent.statusBar.showMessage("create spatially...")
            self.mesh = self.mesh.createH2()

        self.parent.statusBar.showMessage(str(self.mesh))
        self.btn_mesh_export.setEnabled(True)
        self.showMesh()

    def showMesh(self):
        self.parent.plotWidget.axis.cla()
        if self.chbx_mesh_attr.isChecked() is True:
            self.regionGetAttributes()
            show(self.mesh, pg.solver.parseArgToArray(self.attr_map, self.mesh.cellCount(
            ), self.mesh), ax=self.parent.plotWidget.axis)
            show(drawMeshBoundaries(self.parent.plotWidget.axis, self.mesh,
                hideMesh=False),
                ax=self.parent.plotWidget.axis,
                fillRegion=False)
        else:
            show(self.mesh, ax=self.parent.plotWidget.axis)

        self.parent.plotWidget.axis.set_ylim(self.parent.plotWidget.axis.get_ylim()[::-1])
        self.parent.plotWidget.canvas.draw()

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
