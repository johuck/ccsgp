"""
.. module:: ccsgp
   :platform: Unix, Windows
   :synopsis: provides make_plot, repeat_plot (make_plot2D, make_panel)

.. moduleauthor:: Patrick Huck <phuck@lbl.gov>
"""

import numpy as np
from classes import MyPlot

def make_plot(**kwargs):
  """ main function to generate a 1D plot

  - Kwargs:
    name, title, debug,
    data, styles, properties, titles
    key, x(y)label, x(y)r, x(y)log, vert_lines, labels
  - explain format of kwargs.

  :param labels: 'label text': [x-pos., y-pos., abs. placement yes/no]
  :type labels: dict
  :returns: MyPlot
  """
  plt = MyPlot(
    name = kwargs.get('name', 'test'),
    title = kwargs.get('title', ''),
    debug = kwargs.get('debug', 0)
  )
  plt.initData(**kwargs)
  plt.prepare_plot(**kwargs)
  plt.plot()
  return plt

def repeat_plot(plt, name, **kwargs):
  """repeat a plot with different props

  same kwargs as make_plot.

  :param plt: plot to repeat
  :type plt: MyPlot
  :param name: basename of new output file(s)
  :type name: str
  :returns: plt
  """
  plt.gp('set terminal dumb')
  plt.epsname = name + '.eps'
  plt.prepare_plot(**kwargs)
  plt.plot()
  return plt

############################################
## TODO: make_panel is under development! ##
############################################
#
#def make_panel(name='test', log=[False,False], **kwargs):
#  plt = MyPlot(name = name)
#  plt.prepare_multiplot()
#  plt.setLog(log)
#  plt.setAxisRange(0, 1.15)
#  plt.setAxisRange(1e-5, 20, axis = 'y')
#  plt.setMargins(l = 0.3, b = 2, r = 0.5, t = 0.1)
#  #plt.drawLabel('mass', [0.5,0.1])
#  for t, d in kwargs['data'].iteritems(): # TODO: OrderedDict
#    plt.prepare_subfig()
#    plt.initData(
#      data = [d], using = ['1:2:3'], main_opts = ['points'],
#      extra_opts = ['lw 4 lt 1 pt 18', 'lw 4 lt 1 lc 0'],
#      titles = [t]
#    )
#    plt.plot()
#
############################################
