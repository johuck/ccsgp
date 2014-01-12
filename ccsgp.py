"""
.. module:: ccsgp
   :platform: Unix, Windows
   :synopsis: provides make_plot, repeat_plot (make_plot2D, make_panel)

.. moduleauthor:: Patrick Huck <phuck@lbl.gov>
"""

import numpy as np
import uncertainties.unumpy as unp
from .classes import MyPlot, MyPlot2D

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
