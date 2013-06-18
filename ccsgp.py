#!/usr/bin/env python

import os
import numpy
import Gnuplot, Gnuplot.funcutils
from subprocess import call

os.environ['GNUPLOT_PS_DIR'] = os.getcwd()

class MyPlot:
  def __init__(self, data, fdata=None):
    self.pts = Gnuplot.Data(data, inline=1, with_="points pt 18 lw 4 lc 1 ps 2")
    self.err = Gnuplot.Data(data, inline=1, with_="errorbars lc 0 lw 4")
    self.func = None
    if fdata is not None:
      self.func = Gnuplot.Data(fdata, inline=1, with_="lines lc 0 lw 4 lt 1")
    self.gp = Gnuplot.Gnuplot(debug=0)
    self.gp('set terminal dumb')
  def __rng(self, a, b):
    return '[%f:%f]' % (a, b)
  def setEPS(self, n): self.epsname = n
  def setX(self, xt, x1=None, x2=None):
    self.gp.xlabel(xt)
    if x1 is not None and x2 is not None:
      self.gp('set xrange ' + self.__rng(x1, x2))
  def setY(self, yt, y1=None, y2=None):
    self.gp.ylabel(yt)
    if y1 is not None and y2 is not None:
      self.gp('set yrange ' + self.__rng(y1, y2))
  def convert(self):
    pdfname = os.path.splitext(self.epsname)[0] + '.pdf'
    convert_cmd = 'ps2pdf -dEPSCrop %s %s' % (self.epsname, pdfname)
    call(convert_cmd, shell=True)
  def plot(self):
    if self.func is not None:
      self.gp.plot(self.err, self.pts, self.func)
    else:
      self.gp.plot(self.err, self.pts)
    self.gp.hardcopy(self.epsname, enhanced=1, color=1,
                     mode='landscape', fontsize=22)
    self.convert()
