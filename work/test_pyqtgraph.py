# from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import numpy as np

x = np.linspace(0.0, 2 * np.pi, 1000)
y = np.sin(x)
pw = pg.plot(x, y, pen="r")  # plot x vs y in red
y2 = np.cos(x)
y3 = np.tan(x)
# pw.plot(x, y2, pen="b")

# win = pg.GraphicsWindow()  # Automatically generates grids with multiple items
# win.addPlot(data1, row=0, col=0)
# win.addPlot(data2, row=0, col=1)
# win.addPlot(data3, row=1, col=0, colspan=2)

# pg.show(imageData)  # imageData must be a numpy array with 2 to 4 dimensions
