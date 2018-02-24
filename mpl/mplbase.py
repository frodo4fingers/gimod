"""
The matplotlib basiscs for the polygon behaviour.
"""

from matplotlib import pyplot as plt
from matplotlib import patches
from matplotlib import lines
import numpy as np

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QCursor
    from PyQt5.QtCore import Qt

except ImportError:
    from PyQt4.QtGui import QApplication, QCursor
    from PyQt4.Core import Qt


class MPLBase():
    """Hold the general behaviour of the drawn polygons."""

    def __init__(self, parent=None):
        """."""
        self.figure = parent.figure
        self.parent = parent

    def connect(self):
        """."""
        self.cid_p = self.figure.canvas.mpl_connect(
            'button_press_event', self.onPress)
        self.cid_dp = self.figure.canvas.mpl_connect(
            'button_press_event', self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect(
            'motion_notify_event', self.onMotion)
        self.cid_r = self.figure.canvas.mpl_connect(
            'button_release_event', self.onRelease)
        self.cid_ae = self.figure.canvas.mpl_connect(
            'axes_enter_event', self.axesEnter)
        self.cid_al = self.figure.canvas.mpl_connect(
            'axes_leave_event', self.axesLeave)

    def disconnect(self, cid=None):
        """Disconnect all the stored connection ids."""
        if cid is not None:
            self.figure.canvas.mpl_disconnect(getattr(self, cid))
        else:
            for cid in ['cid_p', 'cid_dp', 'cid_m', 'cid_r', 'cid_ae', 'cid_al']:
                if hasattr(self, cid):
                    self.disconnect(cid)

    def axesLeave(self, event):
        """Allow the standard cursors outside the drawing area."""
        QApplication.restoreOverrideCursor()

    def axesEnter(self, event):
        """Prepend matplotlibs new feature to create a QWaitCursor while dragging some stuff."""
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))

    def drawMagnets(self, magnets):
        """
        Todo
        ----
        ATM this is drawn over and not visible... fix this
        """
        x = magnets[:, 0]
        y = magnets[:, 1]
        self.figure.axis.plot(x, y, 'o', c='white', zorder=10)
        self.figure.canvas.draw()

    def drawToCanvas(self, patches):
        """Convenience function to add the gathered path to the current figure."""
        self.figure.axis.cla()
        if self.parent.parent.toolbar.acn_imageAsBackground.isChecked():
            alpha = 0.2
            self.parent.parent.image_tools.setBackground()
        else:
            alpha = 1
        cmap = plt.cm.get_cmap(None, len(patches))
        for i, patch in enumerate(patches):
            # patch.set_fc((*cmap(i)[:3], 0.8))
            patch.set_lw(1)
            if isinstance(patch, lines.Line2D):
                patch.set_color((*cmap(i)[:-1], alpha))
                self.figure.axis.add_line(patch)
            else:
                patch.set_fc((*cmap(i)[:-1], alpha))
                if i > 0:  # everything else than world
                    patch.set_ec('#ffffff')
                else:
                    patch.set_ec('#000000')
                self.figure.axis.add_patch(patch)

        verts = self.parent.magnets[0]
        x = [v[0] for v in verts]
        y = [v[1] for v in verts]
        self.figure.axis.set_xlim([min(x), max(x)])
        self.figure.axis.set_ylim([min(y), max(y)])

        self.figure.canvas.draw()
