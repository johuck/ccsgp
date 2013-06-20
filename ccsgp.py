#!/usr/bin/env python

import os
import numpy as np
import uncertainties.unumpy as unp
import Gnuplot, Gnuplot.funcutils
from subprocess import call

os.environ['GNUPLOT_PS_DIR'] = os.getcwd()

class MyPlot:
  def __init__(self, data, # data = array of numpy arr's [x, y, dy]
               main_opts = ['points'], # len(main_opts) = len(data)
               extra_opts = ['pt 18 lw 4 lc 1', 'lc 0 lw 4'], # len(extra_opts) = 2*len(data)
               titles = ['title1'] # array of key titles
              ):
    self.data = [None]*(2*len(data))
    for i in xrange(len(data)):
      w1 = main_opts[i]+' lc '+str(i)+extra_opts[2*i]
      self.data[2*i] = Gnuplot.Data(data[i], inline=1, title=titles[i], with_ = w1)
      w2 = 'yerrorbars lc '+str(i)+' pt 0 '+extra_opts[2*i+1]
      self.data[2*i+1] = Gnuplot.Data(data[i], inline=1, with_ = w2)
    self.gp = Gnuplot.Gnuplot(debug=0)
    self.gp('set terminal dumb')
    self.gp('set bars small')
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
    self.gp.plot(*self.data)
    self.gp.hardcopy(self.epsname, enhanced=1, color=1,
                     mode='landscape', fontsize=22)
    self.convert()

def getNumpyArr(x, a):
  return np.array((x, unp.nominal_values(a), unp.std_devs(a))).T

def make_plot(name='test', log=False, **kwargs):
  plt = MyPlot(
    data = [
      getNumpyArr(kwargs['x'][i], kwargs['y'][i]) for i in xrange(len(kwargs['y']))
    ],
    main_opts = kwargs['main_opts'],
    extra_opts = kwargs['extra_opts'],
    titles = kwargs['titles']
  )
  plt.setEPS(name+'.eps')
  plt.setX('invariant mass', kwargs['xr'][0], kwargs['xr'][1])
  plt.setY(name, kwargs['yr'][0], kwargs['yr'][1])
  if log is True: plt.gp('set logscale y')
  plt.plot()
