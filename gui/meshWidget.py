# TODO: current state of development... needs to be sorted out
try:
    from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QLineEdit,  QPushButton, QStatusBar, QToolBar, QTabWidget, QSplitter, QAction, QMessageBox
    from PyQt5.QtCore import QSize, Qt
    from PyQt5.QtGui import QIcon

except ImportError:
    from PyQt4.QtGui import QMainWindow, QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QSizePolicy, QCheckBox, QLineEdit,  QPushButton, QStatusBar, QToolBar, QTabWidget, QSplitter, QAction, QMessageBox, QIcon
    from PyQt4.QtCore import QSize, Qt


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
        self.setupWidget()

    def setupWidget(self):
        """Design the layout of the tab that holds the options for tetgen."""
        la_mesh_quality = QLabel("Mesh Quality:")
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
        vbox_mesh_labels.addWidget(la_mesh_quality)
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

        self.setLayout(vbox_mesh)
