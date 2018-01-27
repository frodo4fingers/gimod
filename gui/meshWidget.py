try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QLineEdit,
        QPushButton, QMessageBox, QGridLayout)
    from PyQt5.QtCore import Qt

except ImportError:
    from PyQt4.QtGui import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QLineEdit,
        QPushButton, QMessageBox, QGridLayout)
    from PyQt4.QtCore import Qt

import pygimli as pg
from pygimli import show
from pygimli.meshtools import createMesh
from pygimli.mplviewer import drawMeshBoundaries


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

        # connect the signals to their functions
        self.chbx_mesh_refine.stateChanged.connect(self.changedChbxMeshRefine)
        self.chbx_smooth.stateChanged.connect(self.changedChbxSmooth)
        self.chbx_switches.stateChanged.connect(self.changedChbxSwitches)
        self.btn_mesh.clicked.connect(self.clickedBtnMesh)

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
        self.la_switches.setEnabled(False)
        self.chbx_switches = QCheckBox()
        self.chbx_switches.setEnabled(False)
        self.le_switches = QLineEdit("-pzeAfaq31")
        self.le_switches.setEnabled(False)
        self.switches = None

        # allow colored attribute table overlay together with the mesh
        la_mesh_show_attr = QLabel("Show Attributes:")
        self.chbx_mesh_attr = QCheckBox()

        # the button to hit and run
        self.btn_mesh = QPushButton("mesh")
        self.btn_mesh.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QGridLayout()
        # first row
        layout.addWidget(la_mesh_quality, 0, 0, 1, 1)
        layout.addWidget(self.spb_mesh_quality, 0, 1, 1, 1)
        # second row
        layout.addWidget(la_cell_area, 1, 0, 1, 1)
        layout.addWidget(self.spb_cell_area, 1, 1, 1, 1)
        # third row
        layout.addWidget(la_mesh_refine, 2, 0, 1, 1)
        box_refine = QHBoxLayout()
        box_refine.addWidget(self.chbx_mesh_refine)
        box_refine.addWidget(self.cbx_mesh_refine)
        layout.addLayout(box_refine, 2, 1, 1, 1)
        # fourth row
        layout.addWidget(la_smooth, 3, 0, 1, 1)
        box_smooth = QHBoxLayout()
        box_smooth.addWidget(self.chbx_smooth)
        box_smooth.addWidget(self.cbx_smooth)
        box_smooth.addWidget(self.spb_smooth)
        layout.addLayout(box_smooth, 3, 1, 1, 1)
        # fifth row
        layout.addWidget(self.la_switches, 4, 0, 1, 1)
        box_switch = QHBoxLayout()
        box_switch.addWidget(self.chbx_switches)
        box_switch.addWidget(self.le_switches)
        layout.addLayout(box_switch, 4, 1, 1, 1)
        # sixth row
        layout.addWidget(la_mesh_show_attr, 5, 0, 1, 1)
        layout.addWidget(self.chbx_mesh_attr, 5, 1, 1, 1)

        hbox_mesh_n_export = QHBoxLayout()
        hbox_mesh_n_export.addWidget(self.btn_mesh)
        # hbox_mesh_n_export.addWidget(self.btn_mesh_export)

        vbox_mesh = QVBoxLayout()
        vbox_mesh.addLayout(layout)
        # vbox_mesh.addLayout(hbox_mesh)
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

        self.parent.statusbar.showMessage("generating mesh...")
        self.mesh = createMesh(self.parent.builder.polys, quality=self.spb_mesh_quality.value(
        ), area=self.spb_cell_area.value(), smooth=self.smooth_method, switches=self.switches)

        if self.mesh_refine is True and self.cbx_mesh_refine.currentText() == "quadratic":
            self.parent.statusbar.showMessage("create quadratic...")
            self.mesh = self.mesh.createP2()
        elif self.mesh_refine is True and self.cbx_mesh_refine.currentText() == "spatially":
            self.parent.statusbar.showMessage("create spatially...")
            self.mesh = self.mesh.createH2()

        self.parent.statusbar.showMessage(str(self.mesh))
        self.parent.mb_save_mesh.setEnabled(True)
        self.showMesh()

    def showMesh(self):
        """."""
        self.parent.plotWidget.axis.cla()
        if self.chbx_mesh_attr.isChecked() is True:
            success = False
            # gather the attributes from other tab
            attr_map, success = self.regionGetAttributes()
            if success:
                show(self.mesh, pg.solver.parseArgToArray(
                    attr_map, self.mesh.cellCount(), self.mesh),
                    ax=self.parent.plotWidget.axis
                    )
                show(drawMeshBoundaries(
                    self.parent.plotWidget.axis, self.mesh, hideMesh=False),
                    ax=self.parent.plotWidget.axis,
                    fillRegion=False
                    )
        else:
            success = True
            show(self.mesh, ax=self.parent.plotWidget.axis)

        if success:
            self.parent.plotWidget.canvas.draw()

    def regionGetAttributes(self):
        """
        Reach out to the info table where all polygon information is stored.
        Get the 'Attribute' information for each region and establish a
        attribute map.

        Returns
        -------
        attr_map: List[List[int, float]]
            The attribute map necessary for several purposes (like plotting the
            values of a region (..totally random example))
        """
        # flag for value checking
        success = True
        # get the polygon table
        poly_table = self.parent.info_tree.tw_polys
        # count the listed items(polygons)
        n_polys = poly_table.topLevelItemCount()
        # iterate over them and get the attribute content
        regions = set()
        attrs = []
        for i in range(n_polys):
            # the item in list
            poly = poly_table.topLevelItem(i)
            # # needed is region and attribute
            for k in range(poly.childCount()):
                # identify by name.. marker, angle, start_x
                identifier = poly.child(k).text(0)
                if identifier == 'Marker:':
                    regions.add(int(poly_table.itemWidget(poly.child(k), 1).currentText()))
                if identifier == 'Attributes:':
                    attr = poly.child(k).text(1)
                    try:
                        attrs.append(float(attr))
                        poly.child(k).setForeground(0, Qt.black)
                    except ValueError:
                        # mark missing/wrong values red
                        poly.child(k).setForeground(0, Qt.red)
                        # raised on empty field or characters
                        self.parent.statusbar.showMessage("The value {} could be casted into float. Check your attributes!".format(attr))
                        success = False

        if not success:
            return None, success

        if success:
            # very sloppy check on the attributes
            if len(regions) != len(attrs):
                self.parent.statusbar.showMessage(
                    "Could not cast a few values or a region has been assigned\
                    multiple values. Check your attributes!".format(attr))
                success = False
                return None, success

        if success:
            attr_map = list(zip(regions, attrs))
            return attr_map, success


if __name__ == '__main__':
    pass
