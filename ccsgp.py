import numpy as np
from myplot import MyPlot
from config import ureg, default_size

def make_plot(data, properties, titles, **kwargs):
  """ main function to generate a 1D plot

  * each dataset is represented by a numpy array consisting of data points in
    the format ``[x, y, dx, dy1, dy2]``, dy1 = statistical error, dy2 = systematic uncertainty
  * for symbol numbers to use in labels see http://bit.ly/1erBgIk
  * lines format: `'<x/y>=<value>': '<gnuplot options>'`, horizontal = (along) x, vertical = (along) y
  * labels format: `'label text': [x, y, abs. placement true/false]`
  * arrows format: `[<x0>, <y0>], [<x1>, <y1>], '<gnuplot props>'`

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
  :param lines: vertical and horizontal lines
  :type lines: dict
  :param arrows: arrows
  :type arrows: list
  :param labels: labels
  :type labels: dict
  :param lmargin: defines left margin size (relative to screen)
  :type lmargin: float
  :param bmargin: defines bottom margin size
  :type bmargin: float
  :param rmargin: defines right margin size
  :type rmargin: float
  :param tmargin: defines top margin size
  :type tmargin: float
  :param arrow_offset: offset from data point for special error bars (see gp_panel)
  :type arrow_offset: float
  :param arrow_length: length of arrow from data point towards zero for special error bars (see gp_panel)
  :type arrow_length: float
  :param arrow_bar: width of vertical bar at end of special error bars (see gp_panel)
  :type arrow_bar: float
  :param gpcalls: execute arbitrary gnuplot set commands
  :type gpcalls: list
  :returns: MyPlot
  """
  plt = MyPlot(
    name = kwargs.get('name', 'test'),
    title = kwargs.get('title', ''),
    debug = kwargs.get('debug', 0)
  )
  plt.setErrorArrows(**kwargs)
  plt.setAxisLogs(**kwargs)
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
  plt.setErrorArrows(**kwargs)
  plt.setAxisLogs(**kwargs)
  plt.prepare_plot(**kwargs)
  plt._setter(kwargs.get('gpcalls', []))
  plt.plot()
  return plt

def make_panel(dpt_dict, **kwargs):
  """make a panel plot

  * ``name/title/debug`` are global options used once to initialize the multiplot
  * ``x,yr/x,ylog/lines/labels/gpcalls`` are applied on each subplot
  * ``key/ylabel`` are only plotted in first subplot
  * ``xlabel`` is centered over entire panel
  * same for ``r,l,b,tmargin`` where ``r,lmargin`` will be reset, however, to
    allow for merged y-axes
  * input: OrderedDict w/ subplot titles as keys and lists of make_plot's
    ``data/properties/titles`` as values, see below
  * ``layout`` = '<cols>x<rows>', defaults to horizontal panel if omitted
  * ``key_subplot_id`` sets the desired subplot to put the key in

  :param dpt_dict: ``OrderedDict('subplot-title': [data, properties, titles], ...)``
  :type dpt_dict: dict
  """
  plt = MyPlot(
    name = kwargs.get('name', 'test'),
    title = kwargs.get('title', ''),
    debug = kwargs.get('debug', 0)
  )
  nSubPlots = len(dpt_dict)
  plt.size = kwargs.get('size', default_size)
  height, width = [
      float(ureg.parse_expression(s).to('cm').magnitude)
      for s in plt.size.split(',')
  ]
  text_inch = ureg.parse_expression('24point').to('cm').magnitude
  lm = kwargs.get('lmargin', 2.2*text_inch/width)
  bm = kwargs.get('bmargin', 1.8*text_inch/height)
  rm = kwargs.get('rmargin', 0.99)
  tm = kwargs.get('tmargin', 0.99)
  xlabel, ylabel = kwargs.get('xlabel',''), kwargs.get('ylabel','')
  plt._setter([
    'label 100 "%s" at screen %f,%f rotate center' % (ylabel, lm/2/2.2, (bm+tm)/2),
    'label 101 "%s" at screen %f,%f center' % (xlabel, (lm+rm)/2, bm/2/1.8),
  ])
  nx, ny = nSubPlots, 1 # horizontal panel by default
  layout = kwargs.get('layout')
  if layout is not None: nx, ny = map(int, layout.split('x'))
  w, h = (rm - lm) / nx, (tm - bm) / ny
  nDanglPlots = nSubPlots%nx # number of plots "dangling" in last row
  plt._setter([
    'terminal postscript eps enhanced color "Helvetica" 24 size %fcm,%fcm' % (width, height),
    'output "%s"' % plt.epsname,
    'multiplot layout %d,%d rowsfirst' % (ny, nx)
  ])
  plt.setErrorArrows(**kwargs)
  xgap, ygap = 0.1 / width, 0.1 / height # both in cm
  key_subplot_id = kwargs.get('key_subplot_id', 0)
  if nDanglPlots > 0 and key_subplot_id > len(dpt_dict)-1: # allow for key in dangling panel
      cp_key = dpt_dict.keys()[0]
      xr = kwargs.get('xr') 
      if xr is not None: xfake = xr[0] - 0.5 * (xr[1]-xr[0])
      else: xfake = 1.
      dpt_dict.update({'': [
          [ np.array([[xfake, 1, 0, 0, 0]]) for d in dpt_dict[cp_key][0] ],
          dpt_dict[cp_key][1], dpt_dict[cp_key][2]
      ]})
  for subplot_title, dpt in dpt_dict.iteritems():
    if plt.nLabels > 0: plt.gp('unset label')
    plt.setLabel('{/Helvetica-Bold %s}' % subplot_title, [0.1, 0.9])
    plt.setAxisLogs(**kwargs)
    plt.initData(*dpt, subplot_title = subplot_title)
    plt.prepare_plot(margins=False, **kwargs)
    col, row = plt.nPanels % nx, plt.nPanels / nx
    sub_lm = lm + col * w + xgap/2.
    sub_rm = lm + (col + 1) * w - xgap/2.
    sub_tm = tm - row * h - ygap/2.
    sub_bm = tm - (row + 1) * h + ygap/2.
    plt.gp('unset xlabel')
    plt.gp('unset ylabel')
    if col > 0: plt.gp('set format y " "')
    if ( row < ny-1 and not nDanglPlots ) or (
        row+1 == ny-1 and nDanglPlots and col+1 <= nDanglPlots
    ): plt.gp('set format x " "')
    if plt.nPanels > 0:
      plt.gp('set noarrow')
    if plt.nPanels != key_subplot_id:
      plt.gp('unset key')
    plt.nPanels += 1
    plt._setter([
      'lmargin at screen %f' % sub_lm, 'rmargin at screen %f' % sub_rm,
      'bmargin at screen %f' % sub_bm, 'tmargin at screen %f' % sub_tm
    ] + kwargs.get('gpcalls', []))
    if nDanglPlots > 0 and plt.nPanels-1 == key_subplot_id:
      plt.gp('set format x " "')
      plt.gp('unset border')
      plt.gp('unset xtics')
      plt.gp('unset ytics')
      plt.gp('unset object')
    plt.plot(hardcopy = False)
  plt._hardcopy()
  plt.gp('unset multiplot; set output')
