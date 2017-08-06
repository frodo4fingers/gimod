#!/usr/bin/env python
# encoding: UTF-8


class SpanLine(object):

    def __init__(self, parent=None):
        # super(SpanLine, self).__init__(parent)
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
        self.cidP = self.figure.canvas.mpl_connect('button_press_event', self.onPress)
        self.cidR = self.figure.canvas.mpl_connect('button_release_event', self.onRelease)

    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cidP)
        self.figure.canvas.mpl_disconnect(self.cidR)

    def onPress(self, event):
        if event.button is 1:
            self.xP = event.xdata
            self.yP = event.ydata
            if self.parent.parent.toolBar.acn_magnetizePoly.isChecked() is True:
                if self.parent.mp.xP is not None:
                    self.xP = self.parent.mp.xP
                    self.yP = self.parent.mp.yP
            self.x.append(self.xP)
            self.y.append(self.yP)
            self.line.set_data(self.x, self.y)
            self.figure.canvas.draw()
            self.clicker += 1

    def onRelease(self, event):
        if self.clicker > 0:
            self.line.set_data([0], [0])
            self.parent.printCoordinates(self.x[self.clicker - 1], self.y[self.clicker - 1], self.x[self.clicker], self.y[self.clicker], form="Line")


if __name__ == '__main__':
    pass
