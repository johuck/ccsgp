#!/usr/bin/env python

import os
import numpy
import Gnuplot, Gnuplot.funcutils

os.environ['GNUPLOT_PS_DIR'] = os.getcwd()

class MyPlot:
  def __init__(self, data):
    self.pts = Gnuplot.Data(data, inline=1, with_="points pt 18 lw 4 lc 1 ps 2")
    self.err = Gnuplot.Data(data, inline=1, with_="errorbars lc 0 lw 4")
    self.gp = Gnuplot.Gnuplot(debug=1)
  def setEPS(self, n):
    self.epsname = n
  def setX(self, xt):
    self.gp.xlabel(xt)
  def setY(self, yt):
    self.gp.ylabel(yt)
  def plot(self):
    self.gp.plot(self.err, self.pts)
    self.gp.hardcopy(self.epsname, enhanced=1, color=1,
                     mode='landscape', fontsize=22)
