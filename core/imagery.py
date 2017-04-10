#!/usr/bin/env python
# encoding: UTF-8

import matplotlib.pyplot as plt


class ImageTools():
    """
        Provides the tools for contrast recognition with OpenCV and the
        algorithms to split that into multiple paths or set chosen picture
        as background
    """

    def __init__(self, parent=None):
        self.parent = parent
        self.statusBar = parent.statusBar
        self.threshold1 = parent.toolBar.acn_imageThreshold1.value()
        self.threshold2 = parent.toolBar.acn_imageThreshold2.value()
        self.imagePolys = parent.toolBar.acn_imagePolys
        self.polyDensity = parent.toolBar.acn_imageDensity
        self.fname = parent.fname
        self.figure = parent.figure
        self.background = parent.toolBar.acn_imageAsBackground

    def getContours(self):
        try:
            import cv2
            # read image
            src = cv2.imread(self.fname)
            img = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
            # basic threshold
            th, dst = cv2.threshold(img, float(self.threshold1), float(
            self.threshold2), cv2.THRESH_BINARY)
            # find Contours
            image, contours, hierarchy = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            # sort after polygon area and start with largest area
            paths = sorted(contours, key=cv2.contourArea)[::-1]
            # sort out those structures that are smaller than 6 dots, first one is frame
            self.paths = [i for i in paths if len(i) > 5][1:]
            self.statusBar.showMessage("there are {} possible polygons with current settings".format(len(self.paths)))

            # adjust the spinbox with number of polygons
            self.imagePolys.setRange(1, len(self.paths))
            self.polyDensity.setRange(1, 10)

            # draw initially
            self.polysFromImage()

        except ModuleNotFoundError:
            self.parent.acn_imageAsBackground.setChecked(True)
            self.parent.acn_imageAsBackground.setEnabled(False)

    def polysFromImage(self):
        """
            take only the number of polys chosen in the spinbox
        """
        cutDown = self.paths[:self.imagePolys.value()]
        self.contours = []
        for path in cutDown:
            tuples = []
            for tup in path:
                tuples.append([float(tup[0][0]), float(tup[0][1])])
            self.contours.append(tuples)
        self.dotDensityOfPolygons()

    def dotDensityOfPolygons(self):
        """
            takes every n-th tuple specified by imageDensity spinbox
        """
        self.contoursCutted = []
        for p in self.contours:
            self.contoursCutted.append([p[i] for i in range(0, len(p), self.polyDensity.value())])
        # self.findMinMax()
        self.imagePlot()

    def imagePlot(self):
        self.figure.axis.cla()
        for p in self.contoursCutted:
            self.figure.axis.scatter(*zip(*p), alpha=0.5, s=2)
        self.figure.canvas.draw()

    def setBackground(self):
        """
            set chosen image file as background to draw over
        """
        self.figure.axis.cla()
        img = plt.imread(self.fname)
        self.figure.axis.imshow(img, alpha=0.6)
        self.figure.canvas.draw()


if __name__ == '__main__':
    pass
