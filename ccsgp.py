#!/usr/bin/env python

import os
import numpy
import Gnuplot, Gnuplot.funcutils

os.environ['GNUPLOT_PS_DIR'] = os.getcwd()

class MyPlot:
  def __init__(self, x, y, n, xt, yt):
    self.data = Gnuplot.Data(x, y, inline=1, with_="points pt 18 lw 4 ps 2")
    self.epsname = n
    self.gp = Gnuplot.Gnuplot(debug=1)
    self.gp.xlabel(xt)
    self.gp.ylabel(yt)
  def plot(self):
    self.gp.plot(self.data)
    self.gp.hardcopy(self.epsname, enhanced=1, color=1,
                     mode='landscape', fontsize=22)
