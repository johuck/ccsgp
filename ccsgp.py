#!/usr/bin/env python

import os
import numpy as np
import uncertainties.unumpy as unp
import Gnuplot, Gnuplot.funcutils
from subprocess import call

os.environ['GNUPLOT_PS_DIR'] = os.path.dirname(__file__)

class MyBasePlot(object):
  def __init__(self, title = '', isPanel = False, name = 'test', debug = 0):
    # members
    self.title = title
    self.isPanel = isPanel
    self.name = name
    self.epsname = name + '.eps'
    self.gp = Gnuplot.Gnuplot(debug = debug)
    self.xPanProps = [1.9, 0.23, 0.15] # xscale, xsize, xoffset for panel plots
    self.nPanels = 0
    self.nVertLines = 0
    self.nLabels = 0
    self.posLabelsAbs = True
    self.defaultkey = [
      'spacing 1.4', 'samplen 2.2', 'reverse Left',
      'box lw 2', 'height 0.5', 'font ",22"'
    ]
    # gnuplot setup commands
    self.gp('set bars small')
    self.gp('set grid lt 4 lc rgb "#C8C8C8"')
    self.gp('set title "%s"' % self.title)
    self.setKey()
    if self.isPanel:
      self.gp('set terminal postscript eps enhanced color "Helvetica" 24')
      self.gp('set size %f,1' % self.xPanProps[0])
      self.gp('set output "%s"' % self.epsname)
      self.gp('set multiplot')
    else:
      self.gp('set terminal dumb')
  def setBorders(self, l, b, r, t):
    self.gp(('set lmargin %f') % l)
    self.gp(('set bmargin %f') % b)
    self.gp(('set rmargin %f') % r)
    self.gp(('set tmargin %f') % t)
  def setKey(self, a = None):
    if a is None: a = self.defaultkey
    for s in a: self.gp('set key %s' % s)
  def __rng(self, a, b): return '[%e:%e]' % (a, b)
  def setXRng(self, x1, x2): self.gp('set xrange ' + self.__rng(x1, x2))
  def setYRng(self, y1, y2): self.gp('set yrange ' + self.__rng(y1, y2))
  def setX(self, xt, x1=None, x2=None):
    self.gp.xlabel(xt)
    if x1 is not None and x2 is not None: self.setXRng(x1, x2)
  def setY(self, yt, y1=None, y2=None):
    self.gp.ylabel(yt)
    if y1 is not None and y2 is not None: self.setYRng(y1, y2)
  def setLog(self, log):
    if log[0] is True:
      self.gp('set logscale x')
    else:
      self.gp('unset logscale x')
      self.gp('set format x "%g"')
    if log[1] is True:
      self.gp('set logscale y')
      self.gp('set format y "10^{%L}"')
      self.gp('set grid mytics')
    else:
      self.gp('unset logscale y')
      self.gp('set format y "%g"')
  def drawVertLine(self, x, opts):
    self.nVertLines += 1
    self.gp(
      'set arrow %d from %f,graph(0,0) to %f,graph(1,1) nohead %s' % (
        self.nVertLines, x, x, opts
      )
    )
  def drawLabel(self, s, pos):
    self.nLabels += 1
    pos_cmd = 'at' if self.posLabelsAbs else 'at graph'
    self.gp(
      'set label %d "%s" %s %f, %f' % (
        self.nLabels, s, pos_cmd, pos[0], pos[1]
      )
    )
  def __conv_cmd(self, c, i, o): return '%s %s %s' % (c, i, o)
  def convert(self):
    base = os.path.splitext(self.epsname)[0]
    convert_cmd = self.__conv_cmd(
      'ps2pdf -dEPSCrop', self.epsname, base+'.pdf'
    )
    call(convert_cmd, shell=True)
    for ext in ['.png', '.jpg']:
      convert_cmd = self.__conv_cmd(
        'convert -density 150', base+'.pdf', base+ext
      )
      call(convert_cmd, shell=True)
  def hardcopy(self):
    self.gp.hardcopy(
      self.epsname, enhanced=1, color=1, mode='landscape', fontsize=24
    )
    self.convert()
  def plot(self):
    # make hardcopy of plot + convert to pdf
    self.gp.plot(*self.data)
    if not self.isPanel: self.hardcopy()
  def write(self):
    """ write all data to HDF5 file for
    - easy numpy import -> (savetxt) -> gnuplot
    - export to ROOT objects
    h5py howto:
      - open file: `f = h5py.File(name, 'r')`
      - list datasets: `list(f)`
      - load entire dataset as np arra: `arr = f['dst_name'][...]`
      - NOTE: literally type the 3 dots, replace dset_name
      - np.savetxt format: `fmt = '%.4f %.3e %.3e %.3e'`
      - save array to txt file: `np.savetxt('arr.dat', arr, fmt=fmt)`
    """
    try:
      import h5py
      f = h5py.File(self.name+'.hdf5', 'w')
      for k in self.dataSets: f.create_dataset(k, data=self.dataSets[k])
      f.close()
    except ImportError, e:
      print 'ccsgp.write: install h5py if you want to use this option!'
  def initSettings(self, kwargs):
    self.setBorders(5, 1, 0.1, 0.1)
    self.setX(kwargs['xlabel'], kwargs['xr'][0], kwargs['xr'][1])
    self.setY(kwargs['ylabel'], kwargs['yr'][0], kwargs['yr'][1])
    if 'key' in kwargs: self.setKey(kwargs['key'])
    else: self.gp('unset key')
    if 'vert_lines' in kwargs:
      for x in kwargs['vert_lines']:
        opts = ''
        if 'vert_lines_opts' in kwargs:
          opts = kwargs['vert_lines_opts'][self.nVertLines]
        self.drawVertLine(x, opts)
    if 'posLabelsAbs' in kwargs:
      self.posLabelsAbs = kwargs['posLabelsAbs']
    if 'labels' in kwargs:
      for l in kwargs['labels']: self.drawLabel(l, kwargs['labels'][l])
    self.setLog(kwargs['log'])
    self.plot()
    if 'write' in kwargs and kwargs['write']: self.write()

class MyPlot(MyBasePlot):
  def __init__(self, title = '', isPanel = False, name = 'test', debug = 0):
    super(MyPlot, self).__init__(
      title = title, isPanel = isPanel, name = name, debug = debug
    )
  def initData(
    self, data, # data = array of numpy arr's [x, y, dy]
    main_opts = ['points'], # len(main_opts) = len(data)
    using = ['1:2:3']*2, # specify columns
    extra_opts = ['pt 18 lw 4 lc 1', 'lc 0 lw 4'], # len(extra_opts) = 2*len(data)
    titles = ['title1'] # array of key titles
  ):
    if self.isPanel:
      pan_wdth = self.xPanProps[1] * self.xPanProps[0]
      xorig = self.xPanProps[2] + self.nPanels * pan_wdth
      print self.nPanels, pan_wdth, xorig
      self.gp('set origin %f,0' % xorig)
      self.gp('set size %f,1' % pan_wdth)
      if self.nPanels > 0: self.gp('set ytics format " "')
      self.nPanels += 1
    self.dataSets = dict( (k, v) for k, v in zip(titles, data) if k != '')
    self.data = [None]*(2*len(data))
    for i in xrange(len(data)):
      w1 = main_opts[i]+' '+extra_opts[2*i]
      self.data[2*i+1] = Gnuplot.Data(
        data[i], inline=1, title=titles[i], using=using[i], with_ = w1
      )
      if (
        data[i].T[2].sum() > 0 and
        main_opts[i] != 'boxerrorbars' and
        main_opts[i] != 'yerrorbars'
      ):
        w2 = 'yerrorbars pt 0 '+extra_opts[2*i+1]
        self.data[2*i] = Gnuplot.Data(
          data[i], inline=1, using=using[i], with_ = w2
        )
    self.data = filter(None, self.data)

class MyPlot2D(MyBasePlot):
  def initData(self, data):
    self.data = Gnuplot.Data(data, inline=1, with_ = 'image')

def getNumpyArr(x, a, bw):
  return np.array((x, unp.nominal_values(a), unp.std_devs(a), bw)).T

def make_plot(name = 'test', title = '', **kwargs):
  """ main function to generate a plot
  describe keyword arguments
  data
  nVertLines
  nLabels
  format conversions
  hdf5 write
  """
  if 'data' in kwargs:
    data = [ kwargs['data'][i] for i in xrange(len(kwargs['data'])) ]
  else:
    data = [
      getNumpyArr(kwargs['x'][i], kwargs['y'][i], kwargs['bw'][i])
      for i in xrange(len(kwargs['y']))
    ]
  plt = MyPlot(
    title, name = name,
    debug = kwargs['debug'] if 'debug' in kwargs else 0
  )
  plt.initData(
    data = data,
    using = kwargs['using'],
    main_opts = kwargs['main_opts'],
    extra_opts = kwargs['extra_opts'],
    titles = kwargs['titles']
  )
  plt.initSettings(kwargs)
  return plt

def make_plot2D(name = 'test', title = '', **kwargs):
  plt = MyPlot2D(title)
  plt.initData(kwargs['data'])
  plt.initSettings(kwargs)
  return plt

def repeat_plot(plt, **kwargs):
  plt.gp('set terminal dumb')
  xr, yr = kwargs['xr'], kwargs['yr']
  plt.setXRng(xr[0], xr[1])
  plt.setYRng(yr[0], yr[1])
  plt.epsname = kwargs['name'] + '.eps'
  plt.setLog(kwargs['log'])
  plt.plot()

def make_panel(name='test', log=[False,False], **kwargs):
  plt = MyPlot(isPanel=True, name=name)
  plt.setLog(log)
  plt.setXRng(0,1.15)
  plt.setYRng(1e-5, 20)
  plt.setBorders(0.3, 2, 0.5, 0.1)
  #plt.drawLabel('mass', [0.5,0.1])
  for t, d in kwargs['data'].iteritems(): # TODO: OrderedDict
    plt.initData(
      data = [d], using = ['1:2:3'], main_opts = ['points'],
      extra_opts = ['lw 4 lt 1 pt 18', 'lw 4 lt 1 lc 0'],
      titles = [t]
    )
    plt.plot()
