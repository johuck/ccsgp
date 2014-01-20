import numpy as np
from myplot import MyPlot

def make_plot(data, properties, titles, **kwargs):
  """ main function to generate a 1D plot

  * each dataset is represented by a numpy array consisting of data points in
    the format ``[x, y, dx, dy]``
  * for symbol numbers to use in labels see http://bit.ly/1erBgIk

  :param data: datasets 
  :type data: list
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
  :param lines: vertical and horizontal lines, format `'<x/y>=<x-value>':
    '<gnuplot options>'`, horizontal = (along) x, vertical = (along) y
  :type lines: dict
  :param labels: labels, format `'label text': [x, y, abs. placement true/false]`
  :type labels: dict
  :param lmargin: defines left margin size (relative to screen)
  :type lmargin: float
  :param bmargin: defines bottom margin size
  :type bmargin: float
  :param rmargin: defines right margin size
  :type rmargin: float
  :param tmargin: defines top margin size
  :type tmargin: float
  :param gpcalls: execute arbitrary gnuplot set commands
  :type gpcalls: list
  :returns: MyPlot
  """
  plt = MyPlot(
    name = kwargs.get('name', 'test'),
    title = kwargs.get('title', ''),
    debug = kwargs.get('debug', 0)
  )
  plt.initData(data, properties, titles)
  plt.prepare_plot(**kwargs)
  plt._setter(kwargs.get('gpcalls', []))
  plt.plot()
  return plt

def repeat_plot(plt, name, **kwargs):
  """repeat a plot with different properties (kwargs see make_plot)

  :param plt: plot to repeat
  :type plt: MyPlot
  :param name: basename of new output file(s)
  :type name: str
  :returns: plt
  """
  plt.gp('set terminal dumb')
  plt.epsname = name + '.eps'
  plt.prepare_plot(**kwargs)
  plt._setter(kwargs.get('gpcalls', []))
  plt.plot()
  return plt

def make_panel(dpt_dict, **kwargs):
  """make a panel plot

  * ``name/title/debug`` are global options used once to initialize the multiplot
  * ``key/x,ylabel/x,yr/x,ylog/lines/labels/gpcalls`` are applied on each subplot
  * same for ``r,l,b,tmargin`` where ``r,lmargin`` will be reset, however, to
    allow for merged y-axes
  * open questions:
    * each subplot has a "title" / summarizing label (e.g. energy)
      => show as title or label w/ position?
    * where to show legend?
    * separate or merged x-axis labels?

  :param dpt_dict: OrderedDict w/ subplot titles as keys and lists of
                   make_plot's ``data/properties/titles`` as values, e.g.
                  ``OrderedDict('subplot-title': [data, properties, titles], ...)``
  :type dpt_dict: dict
  """
  plt = MyPlot(
    name = kwargs.get('name', 'test'),
    title = kwargs.get('title', ''),
    debug = kwargs.get('debug', 0)
  )
  nSubPlots = len(dpt_dict)
  plt._setter([
    'terminal postscript eps enhanced color "Helvetica" 24', # TODO: size 10cm,15cm
    'output "%s"' % plt.epsname,
    'multiplot layout 1,%d rowsfirst' % nSubPlots
  ])
  gap = 0.01
  for subplot_title, dpt in dpt_dict.iteritems():
    # TODO: do something with subplot_title
    plt.initData(*dpt)
    plt.prepare_plot(**kwargs)
    lm = kwargs.get('lmargin', default_margins['lmargin'])
    rm = kwargs.get('rmargin', default_margins['rmargin'])
    w = (rm - lm) / nSubPlots
    self._setter([
      'lmargin %f' % (lm + self.nPanels * w + gap/2.),
      'rmargin %f' % (lm + (self.nPanels + 1) * w - gap/2.)
    ])
    if self.nPanels > 0: self.gp('unset ytics')
    plt._setter(kwargs.get('gpcalls', []))
    plt.plot()
    self.nPanels += 1
  self.gp('unset multiplot; set output')
