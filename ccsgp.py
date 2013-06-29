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
               using = ['1:2:3']*2, # specify columns
               extra_opts = ['pt 18 lw 4 lc 1', 'lc 0 lw 4'], # len(extra_opts) = 2*len(data)
               titles = ['title1'] # array of key titles
              ):
    self.nVertLines = 0
    self.nLabels = 0
    self.data = [None]*(2*len(data))
    for i in xrange(len(data)):
      w1 = main_opts[i]+' '+extra_opts[2*i]
      self.data[2*i] = Gnuplot.Data(
        data[i], inline=1, title=titles[i], using=using[i], with_ = w1
      )
      if (
        data[i].T[2].sum() > 0 and
        main_opts[i] != 'boxerrorbars' and
        main_opts[i] != 'yerrorbars'
      ):
        w2 = 'yerrorbars pt 0 '+extra_opts[2*i+1]
        self.data[2*i+1] = Gnuplot.Data(
          data[i], inline=1, using=using[i], with_ = w2
        )
    self.data = filter(None, self.data)
    self.gp = Gnuplot.Gnuplot(debug=0)
    self.gp('set terminal dumb')
    self.gp('set bars small')
    self.gp('set grid lt 4 lc rgb "#C8C8C8"')
    self.gp('set key spacing 1.4')
    self.gp('set key samplen 2.2')
    self.gp('set key reverse Left')
    self.gp('set key box lw 2')
    #self.gp('set key width -4.1')
    self.gp('set key height 0.5')
    self.gp('set title "Evaluated Materials"')
    self.gp('set bmargin 1')
    self.gp('set tmargin 0.1')
    self.gp('set lmargin 3')
    self.gp('set rmargin 0.1')
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
  def drawVertLine(self, x):
    self.nVertLines += 1
    self.gp(
      'set arrow %d from %f,graph(0,0) to %f,graph(1,1) nohead' % (
        self.nVertLines, x, x
      )
    )
  def drawLabel(self, s, pos):
    self.nLabels += 1
    self.gp(
      'set label %d "%s" at %f, %f' % (self.nLabels, s, pos[0], pos[1])
    )
  def convert(self):
    pdfname = os.path.splitext(self.epsname)[0] + '.pdf'
    convert_cmd = 'ps2pdf -dEPSCrop %s %s' % (self.epsname, pdfname)
    call(convert_cmd, shell=True)
  def plot(self):
    self.gp.plot(*self.data)
    self.gp.hardcopy(
      self.epsname, enhanced=1, color=1, mode='landscape', fontsize=24
    )
    self.convert()

def getNumpyArr(x, a, bw):
  return np.array((x, unp.nominal_values(a), unp.std_devs(a), bw)).T

def make_plot(name='test', log=[False,False], **kwargs):
  if 'data' in kwargs:
    data = [ kwargs['data'][i] for i in xrange(len(kwargs['data'])) ]
  else:
    data = [
      getNumpyArr(kwargs['x'][i], kwargs['y'][i], kwargs['bw'][i])
      for i in xrange(len(kwargs['y']))
    ]
  plt = MyPlot(
    data = data,
    using = kwargs['using'],
    main_opts = kwargs['main_opts'],
    extra_opts = kwargs['extra_opts'],
    titles = kwargs['titles']
  )
  plt.setEPS(name+'.eps')
  plt.setX(kwargs['xlabel'], kwargs['xr'][0], kwargs['xr'][1])
  plt.setY(kwargs['ylabel'], kwargs['yr'][0], kwargs['yr'][1])
  if 'vert_lines' in kwargs:
    for x in kwargs['vert_lines']: plt.drawVertLine(x)
  if 'labels' in kwargs:
    for l in kwargs['labels']: plt.drawLabel(l, kwargs['labels'][l])
  if log[0] is True:
    plt.gp('set logscale x')
    plt.gp('set format x "10^{%L}"')
  if log[1] is True:
    plt.gp('set logscale y')
    #plt.gp('set format y "10^{%L}"')
    plt.gp('set grid mytics')
    plt.gp('set ytics ("" .7,"" .8,"" .9, 1, 2, 3, 4, 5, 6, 7)')
  plt.plot()
