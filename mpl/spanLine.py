#!/usr/bin/env python
# encoding: UTF-8


class SpanLine():
    """
    Provide the visualization for creating a PolyLine.

    Todo
    ----
    Add helper line like in spanPoly
    """

    def __init__(self, parent=None):
        """
        Initialize all important variables for matplotlib drawing.

        Parameters
        ----------
        parent: :class:`~core.builder.Builder`
        """
        self.gimod = parent.parent
        self.parent = parent
        self.figure = self.parent.figure
        # introduce empty line to start with
        line, = self.figure.axis.plot([0], [0], c='blue')
        self.x = []
        self.y = []
        self.line = line
        self.clicker = -1
        self.onPress = self.onPress

    def connect(self):
        """Connect all events needed for line drawing."""
        self.cid_p = self.figure.canvas.mpl_connect(
            'button_press_event', self.onPress)
        self.cid_r = self.figure.canvas.mpl_connect(
            'button_release_event', self.onRelease)

    def disconnect(self):
        """Disconnect all the stored connection ids."""
        self.figure.canvas.mpl_disconnect(self.cid_p)
        self.figure.canvas.mpl_disconnect(self.cid_r)

    def onPress(self, event):
        """Collect the event data to later pass on to the PolyLine."""
        if event.button is 1:
            self.x_p = event.xdata
            self.y_p = event.ydata
            # snap current position to nearest node if magnetized
            # this will override the just collected event data
            if self.gimod.toolBar.acn_magnetizePoly.isChecked() is True:
                if self.parent.mp.x_p is not None:
                    self.x_p = self.parent.mp.x_p
                    self.y_p = self.parent.mp.y_p
            self.x.append(self.x_p)
            self.y.append(self.y_p)
            self.line.set_data(self.x, self.y)
            self.figure.canvas.draw()
            self.clicker += 1

    def onRelease(self, event):
        """Reset the line and send the necessary data to build the PolyLine."""
        if self.clicker > 0:
            self.line.set_data([0], [0])
            self.parent.printCoordinates(
                self.x[self.clicker - 1], self.y[self.clicker - 1],
                self.x[self.clicker], self.y[self.clicker], form="Line"
            )


if __name__ == '__main__':
    pass
