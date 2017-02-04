#!/usr/bin/env python
# encoding: UTF-8


class SpanLine():

    def __init__(self, plot):
        # super(SpanLine, self).__init__(parent)
        self.figure = plot
        # introduce empty line to start with
        line, = self.figure.axis.plot([0], [0])
        self.line = line
        self.background = None
        self.onPress = self.onPress

    def connect(self):
        # self.clicked = 1
        self.cid_p = self.figure.canvas.mpl_connect("button_press_event", self.onPress)
        self.cid_m = self.figure.canvas.mpl_connect("motion_notify_event", self.onMotion)
        self.cid_r = self.figure.canvas.mpl_connect("button_release_event", self.onRelease)

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cid_p)
        self.figure.canvas.mpl_disconnect(self.cid_m)
        self.figure.canvas.mpl_disconnect(self.cid_r)

    def getXY(self):
        """
            return spanning coordinates
        """
        return self.x_p, self.y_p, self.x_r, self.y_r

    def onPress(self, event):
        if event.button is 1:
            self.x_p = event.xdata
            self.y_p = event.ydata
            self.line.set_animated(True)
            self.figure.canvas.draw()
            self.background = self.figure.canvas.copy_from_bbox(self.line.axes.bbox)
            self.line.axes.draw_artist(self.line)
            self.figure.canvas.blit(self.line.axes.bbox)

    def onMotion(self, event):
        if event.inaxes != self.line.axes: return
        try:
            self.x_m = event.xdata
            self.y_m = event.ydata
            self.line.set_data([self.x_p, self.x_m], [self.y_p, self.y_m])
            # TODO: den radius am ansatzpunkt anzeigen
            # self.figure.axis.annotate(self.distance(), xy=(self.x_p, self.y_p))

            self.figure.canvas.restore_region(self.background)
            self.line.axes.draw_artist(self.line)
            self.figure.canvas.blit(self.line.axes.bbox)

        except (AttributeError, TypeError):
            pass

    def onRelease(self, event):
        print("release")
        try:
            self.x_r = event.xdata
            self.y_r = event.ydata
            # set line empty to remove from view
            self.line.set_data([0], [0])
            self.line.axes.draw_artist(self.line)
            # set back variables
            self.line.set_animated(False)
            self.background = None
            self.figure.canvas.draw()

        except AttributeError:
            pass


if __name__ == "__main__":
    pass
