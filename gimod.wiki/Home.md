Welcome to the GIMod wiki! Here the whole GUI will be explained and guided through thoroughly (I hope!)

## starting with a sketch you made
since model creation might be time intensive by hand you can set your chosen image as background and draw the paint polygons at least thats the aim for now - does not work as desired...


What works quite fine is the recognition of certain contrasts of the given image. You load it and set the lower and upper threshold via the first two spin boxes.


If the outcome is satisfactory you can set the point density via the third widget. Since every dot will be a node in the later mesh, it makes sense to reduce the density.


The information in the statusbar points out how many polygons were found by the algorithm [OpenCV](http://opencv.org/downloads.html) provides. The fourth widget holds the tool to show more of the found polygons.


If all that is selected you hit the play button and the structure will be converted to a polygon.
