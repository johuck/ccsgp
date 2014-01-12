"""
.. module:: ccsgp
   :platform: Unix, Windows
   :synopsis: provides make_plot, repeat_plot (make_plot2D, make_panel)

.. moduleauthor:: Patrick Huck <phuck@lbl.gov>
"""

import numpy as np
from myplot import MyPlot

def make_plot(data, styles, properties, titles, **kwargs):
  """ main function to generate a 1D plot

  .. note::
     each dataset is represented by a numpy.array consisting of data points in
     the format `[x, y, y_err, bin_width]`

  .. note::
     possible gnuplot styles: points, lines, linespoints, yerrorbars,
     boxerrorbars

  :param data: datasets 
  :type data: list
  :param styles: gnuplot styles for each dataset
  :type styles: list
  :param properties: gnuplot property strings for each dataset (lc, lw, pt ...)
  :type properties: list
  :param titles: legend/key titles for each dataset
  :type titles: list

  :param name: basename of output files
  :type name: str
  :param title: image title
  :type title: str
  :param debug: flag to switch to debug/verbose mode
  :type debug: bool
  :param key: legend/key options to be applied on top of default_key
  :type key: list
  :param xlabel: label for x-axis
  :type xlabel: str
  :param ylabel: label for y-axis
  :type ylabel: str
  :param xr: x-axis range
  :type xr: list
  :param yr: y-axis range
  :type yr: list
  :param xlog: make x-axis logarithmic
  :type xlog: bool
  :param ylog: make y-axis logarithmic
  :type ylog: bool
  :param vert_lines: vertical lines, format `'<x-value>': '<gnuplot style options>'`
  :type vert_lines: dict
  :param labels: labels, format `'label text': [x, y, abs. placement true/false]`
  :type labels: dict
  :returns: MyPlot
  """
  plt = MyPlot(
    name = kwargs.get('name', 'test'),
    title = kwargs.get('title', ''),
    debug = kwargs.get('debug', 0)
  )
  plt.initData(data, styles, properties, titles)
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
