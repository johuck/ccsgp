import os, re, sys
import Gnuplot, Gnuplot.funcutils
from subprocess import call
from utils import zip_flat
from config import basic_setup, supported_styles, ureg, default_size
import numpy as np
from collections import deque

os.environ['GNUPLOT_PS_DIR'] = os.path.dirname(__file__)

class MyPlot(object):
  """base class

  - basic gnuplot setup (bars, grid, title, key, terminal, multiplot)
  - utility functions for general plotting

  :param title: image title
  :type title: str
  :param name: basename used for output files
  :type name: str
  :param debug: debug flag for verbose gnuplot output
  :type debug: bool
  :ivar name: basename for output files
  :ivar epsname: basename + '.eps'
  :ivar gp: Gnuplot.Gnuplot instance
  :ivar nPanels: number of panels in a multiplot
  :ivar nVertLines: number of vertical lines
  :ivar nLabels: number of labels
  :ivar nArrows: number of arrows
  :ivar axisLog: flags for logarithmic axes
  :ivar axisRange: axis range for respective axis (set in setAxisRange)
  """
  def __init__(self, name = 'test', title = '', debug = 0):
    self.name = name
    self.epsname = name + '.ps'
    self.gp = Gnuplot.Gnuplot(debug = debug)
    self.nPanels = 0
    self.nVertLines = 0
    self.nLabels = 0
    self.nArrows = 0
    self.axisLog = { 'x': False, 'y': False }
    self.axisRange = { 'x': [], 'y': [] }
    self.arrow_offset = 0.85
    self.arrow_length = 0.2
    self.arrow_bar = 0.005
    self.dataSets = {}
    self.size = None
    self._setter(['title "%s"' % title] + basic_setup)

  def _clamp(self, val, minimum = 0, maximum = 255):
    """convenience function to clamp number into min..max range"""
    if val < minimum: return minimum
    if val > maximum: return maximum
    return val

  def _colorscale(self, hexstr, scalefactor = 1.4):
    """Scales a hex string by ``scalefactor``. Returns scaled hex string.

    * taken from T. Burgess_ (source_)
    * To darken the color, use a float value between 0 and 1.
    * To brighten the color, use a float value greater than 1.

    >>> colorscale("#DF3C3C", .5)
    #6F1E1E
    >>> colorscale("#52D24F", 1.6)
    #83FF7E
    >>> colorscale("#4F75D2", 1)
    #4F75D2

    .. _source: http://thadeusb.com/weblog/2010/10/10/python_scale_hex_color
    .. _Burgess: http://thadeusb.com/about
    """
    if scalefactor < 0 or len(hexstr) != 6: return hexstr
    r, g, b = int(hexstr[:2], 16), int(hexstr[2:4], 16), int(hexstr[4:], 16)
    r = self._clamp(r * scalefactor)
    g = self._clamp(g * scalefactor)
    b = self._clamp(b * scalefactor)
    return 'rgb "#%02x%02x%02x"' % (r, g, b)

  def _get_style_mod_prop(self, prop):
    """get style and modified property string"""
    m = re.compile('^with \w+').search(prop)
    style = m.group()[5:] if m else 'points'
    mod_prop = re.sub(m.group(), '', prop) if m else prop
    return style, mod_prop

  def _using(self, data, prop = None):
    """determine string with columns to use

    :param data: one dataset
    :type data: numpy.array
    :param prop: property string of a dataset
    :type prop: str
    :returns: '1:2:3', '1:2:4' or '1:2:3:4'
    """
    if not prop: # primary errors
      return ':'.join([
        '%d' % (i+1) for i in xrange(4)
        if i < 2 or (i >= 2 and self.error_sums[i-2] > 0)
      ])
    else: # secondary errors
      # filledcurves or candlesticka
      style, mod_prop = self._get_style_mod_prop(prop)
      if style == 'filledcurves':
        return '1:($2-$5):($2+$5)'
      else:
        low_lim = '(($2-$5)>0)?($2-$5):1e-20' \
                if self.axisLog['y'] else '($2-$5)'
        return '1:%s:2:2:($2+$5)' % low_lim

  def _with_main(self, prop):
    """get the correct property string for main data"""
    style, mod_prop = self._get_style_mod_prop(prop)
    if style not in supported_styles:
      raise Exception('gnuplot style %s not yet supported!' % style)
    style = 'linespoints' if style == 'filledcurves' else style
    return ' '.join([style, mod_prop])

  def _sum_errs(self, data, i):
    """convenience function to calculate sum of i-th column"""
    return data[:, i].sum()

  def _plot_errs(self, data):
    """determine whether to plot primary errors separately

    plot errorbars if data has more than two columns which are not all zero

    :param data: one dataset
    :type data: numpy.array 
    :var error_sums: sum of x and y errors
    :returns: True or False
    """
    if data.shape[1] > 5 or data.shape[1] == 3:
      raise Exception(
        '%d columns not allowed, use either 2, 4 or 5!' % data.shape[1]
      )
    if data.shape[1] < 3: return False
    self.error_sums = [ self._sum_errs(data, i+2) for i in xrange(2) ]
    return (sum(self.error_sums) > 0)

  def _plot_syserrs(self, data):
    """determine whether to plot secondary errors

    :param data: one dataset
    :type data: numpy.array
    :returns: True or False
    """
    return data.shape[1] == 5 and self._sum_errs(data, 4) > 0

  def _with_errs(self, data, prop):
    """generate special property string for primary errors

    * currently error bars are drawn in black
    * use same linewidth as for points
    * TODO: give user the option to draw error bars in lighter color
      according to the respective data points

    :param data: one dataset
    :type data: numpy.array
    :param prop: property string of a dataset
    :type prop: str
    :returns: property string for primary errors
    """
    m = re.compile('lw \d').search(prop)
    lw = m.group()[-1] if m else '1'
    xy = ''.join([
      axis for axis in ['x', 'y']
      if self.error_sums[int(axis=='y')] > 0
    ])
    # TODO: get linewidth for errorbar arrows?
    return '%serrorbars pt 0 lt 1 lc 0 lw %s' % (xy, lw)

  def _with_syserrs(self, prop):
    """generate special property string for secondary errors

    * draw box in lighter color than point/line color
    * does not support integer line colors, only hex

    :param prop: property string of a dataset
    :type prop: str
    :returns: property string for secondary errors
    """
    m = re.compile('lc \d').search(prop)
    if m:
      raise Exception(
        '"%s" not supported! use default_colors or hex specification' % m.group()
      )
    m_lc = re.compile('lc rgb "#[A-Fa-f0-9]{6}"').search(prop)
    lc = self._colorscale(m_lc.group()[-7:-1]) if m_lc else '0'
    m_lw = re.compile('lw \d').search(prop)
    lw = m_lw.group()[-1] if m_lw else '1'
    style, mod_prop = self._get_style_mod_prop(prop)
    style = 'filledcurves' if style == 'filledcurves' else 'candlesticks'
    return '%s fs solid lw %s lt 1 lc %s' % (style, lw, lc)

  def _prettify(self, str):
    """prettify string, remove special symbols"""
    return re.compile(ur'[\W]+',re.UNICODE).sub('_',str.strip())

  def initData(self, data, properties, titles, subplot_title = None):
    """initialize the data

    - all lists given as parameters must have the same length.
    - each data set is drawn twice to allow for different colors for the errorbars
    - error bars use the same linewidth as data points and line color black
    - use 'boxwidth 0.03 absolute' in gp_calls to set the width of the
      uncertainty boxes
    - use alternative gnuplot style if ``properties`` contains a style
      specification in the form ``with <style>`` and if the style is in
      ccsgp.config.supported_styles (style specification has to be at the
      beginning of the property string!)

    :param data: data points w/ format [x, y, dx, dy] for each dataset
    :type data: list of numpy arrays
    :param properties: plot properties for each dataset (pt/lw/ps/lc...)
    :type properties: list of str
    :param titles: key/legend titles for each dataset
    :type titles: list of strings
    :param subplot_title: subplot title for panel plot case
    :type subplot_title: str
    :var dataSets: zipped titles and data for hdf5/ascii output and setAxisRange
    :var data: list of Gnuplot.Data including extra data sets for error plotting
    """
    # dataSets used in _hdf5/_ascii and setAxisRange
    for i, (k, v) in enumerate(zip(titles, data)):
      key = k if k else 'graph' + str(i)
      if subplot_title is not None: # multiplot
        key = '_'.join([subplot_title, key])
      if key in self.dataSets:
        raise ValueError("duplicate key '{0}'!".format(k))
      else:
        self.dataSets[key] = v
    # plot arrows for data points with error bars larger than resp. value
    # TODO: lw/lt/lc are hardcoded! same for arrow length and offset.
    arr_upp_prop = 'head size screen %g,90 lw 4 lt 1 lc 0 front' % self.arrow_bar
    arr_low_prop = 'head empty lw 4 lt 1 lc 0 front'
    if self.axisLog['y']:
      for d in data:
        mask =  d[:,1] - d[:,3] < 0
        for dp in d[mask]:
          arr_start = [ dp[0], dp[1] + dp[3] ]
          if dp[1] > 0:
            self.setArrow(
              [ dp[0], dp[1] / self.arrow_offset ], arr_start, arr_upp_prop
            )
            self.setArrow(
              [ dp[0], dp[1] * self.arrow_offset ],
              [ dp[0], self.arrow_length * dp[1] ], arr_low_prop
            )
          elif arr_start[1] > 0:
            self.setArrow(
              [dp[0], (self.arrow_length + 0.1) * arr_start[1]], arr_start, arr_upp_prop
            )
            self.setArrow(
              arr_start, [dp[0], self.arrow_length * arr_start[1]], arr_low_prop
            )
          else: print 'point omitted:', dp
        d[:,3][mask] = 0
    # zip all input parameters for easier looping
    zipped = zip(data, properties, titles)
    # main data points drawn last
    main_data = [
      Gnuplot.Data(
        d, inline = 1, title = t, using = '1:2',
        with_ = self._with_main(p)
      ) for d, p, t in zipped
    ]
    # extra data set to plot "primary" errors separately
    prim_errs = [
      Gnuplot.Data(
        d, inline = 1, using = self._using(d),
        with_ = self._with_errs(d, p)
      ) if self._plot_errs(d) else None
      for d, p, t in zipped
    ]
    # extra data set for "secondary" errors (systematic uncertainties)
    sec_errs = [
      Gnuplot.Data(
        d, inline = 1, using = self._using(d, p),
        with_ = self._with_syserrs(p)
      ) if self._plot_syserrs(d) else None
      for d, p, t in zipped
    ]
    # zip main & secondary data and filter out None's
    self.data = deque(filter(None, zip_flat(sec_errs, prim_errs, main_data)))

  def _setter(self, list):
    """convenience function to set a list of gnuplot options

    :param list: list of strings given to gnuplot's set command
    :type list: list
    """
    for s in list: self.gp('set %s' % s)

  def setMargins(self, **kwargs):
    """set the margins
    
    * keys other than l(b,t,r)margin are ignored
    * if margin not given leave to gnuplot
    """
    order = ['l', 'b', 'r', 't']
    margins = dict((k, kwargs.get(k+'margin')) for k in order)
    self._setter([
        '%smargin at screen %f' % (k,v)
        for k,v in margins.items()
        if v is not None
    ])

  def setKeyOptions(self, key_opts):
    """set key options

    :param key_opts: strings for key/legend options
    :type key_opts: list
    """
    self._setter(['key %s' % s for s in key_opts])

  def setAxisRange(self, rng, axis = 'x'):
    """set range for specified axis

    * automatically determines axis range to include all data points if range is
      not given.
    * logscale and secondary errors taken into account
    * y-axis range determined for points within given x-axis range

    :param rng: lower and upper range limits
    :type rng: list
    :param axis: axis to which to apply range
    :type axis: str
    """
    if rng is None:
      col = int(axis == 'y')
      all_data = self.dataSets.values()
      vals = np.array([ n for v in all_data for n in v[:, col] ])
      evals = np.zeros(len(vals))
      if axis == 'y':
        evals = np.array([
          max(n) if v.shape[1] >= 4 else 0.
          for v in all_data for n in v[:, 3:]
        ])
        xvals = all_data[0][:, 0]
        mask = (xvals > self.axisRange['x'][0]) & (xvals < self.axisRange['x'][1])
        vals = vals[mask]
        evals = evals[mask]
      axMin = (vals-evals).min()
      if self.axisLog[axis] and not axMin > 0: axMin = vals.min()
      axMax = (vals+evals).max()
      add_rng = 0.1 * (axMax - axMin)
      rng = [
        axMin - add_rng if not self.axisLog[axis] else 0.9 * axMin,
        axMax + add_rng if not self.axisLog[axis] else 1.1 * axMax,
      ]
    self.axisRange[axis] = rng
    self.gp('set %srange [%e:%e]' % (axis, rng[0], rng[1]))

  def setAxisLabel(self, label, axis = 'x'):
    """set label for specified axis

    :param label: label
    :type label: str
    :param axis: axis which to label
    :type axis: str
    """
    self.gp('set %slabel "%s"' % (axis, label))

  def setAxisLog(self, log, axis = 'x'):
    """set logarithmic scale for specified axis

    :param log: whether to set logarithmic
    :type log: bool
    :param axis: axis which to set logarithmic
    :type axis: str
    """
    self.axisLog[axis] = log
    if log:
      self._setter([
        'logscale %s' % axis, 'grid m%stics' % axis,
        'format {0} "10^{{%L}}"'.format(axis)
      ])
    else:
      self.gp('unset logscale %s' % axis)
      self.gp('set format {0} "%g"'.format(axis))

  def setAxisLogs(self, **kwargs):
    """set axes logarithmic if requested"""
    for axis in ['x', 'y']:
      self.setAxisLog(kwargs.get(axis + 'log'), axis = axis)

  def setVerticalLine(self, x, opts):
    """draw a vertical line

    :param x: position on x-axis
    :type x: float
    :param opts: line draw options
    :type opts: str
    """
    self.nVertLines += 1
    self.gp(
      'set arrow %d from %f,graph(0,0) to %f,graph(1,1) nohead %s' % (
        self.nVertLines, x, x, opts
      )
    )

  def addHorizontalLine(self, y, opts):
    """draw horizontal line

    :param y: y-position
    :type y: float
    :param opts: line draw options
    :type opts: str
    """
    d = np.array([ [self.axisRange['x'][i], y] for i in xrange(2) ])
    self.data.appendleft(Gnuplot.Data(
      d, inline = 1, title = '', using = '1:2', with_ = ' '.join(['lines', opts])
    ))

  def setLabel(self, label, pos, abs_place = False):
    """draw a label into the figure

    :param label: label
    :type label: str
    :param pos: x,y - position
    :type pos: list
    :param abs_place: absolute or relative placement
    :type abs_place: bool
    """
    self.nLabels += 1
    place = 'at' if abs_place else 'at graph'
    self.gp(
      'set label %d "%s" %s %f, %f' % (
        self.nLabels, label, place, pos[0], pos[1]
      )
    )

  def setArrow(self, p0, p1, prop):
    """draw an arrow into the figure

    :param p0: start point [x, y]
    :type p0: list
    :param p1: end point [x, y]
    :type p1: list
    :param prop: gnuplot property string for the arrow
    :type prop: str
    """
    self.nArrows += 1
    self.gp(
      'set arrow %d from %g,%g to %g,%g %s' % (
        self.nArrows, p0[0], p0[1], p1[0], p1[1], prop
      )
    )

  def setErrorArrows(self, **kwargs):
    """reset properties of arrows used to plot special errors"""
    self.arrow_offset = kwargs.get('arrow_offset', self.arrow_offset)
    self.arrow_length = kwargs.get('arrow_length', self.arrow_length)
    self.arrow_bar = kwargs.get('arrow_bar', self.arrow_bar)

  def prepare_plot(self, margins=True, **kwargs):
    """prepare for plotting (calls all members of MyPlot)"""
    if self.size is None:
        self.size = kwargs.get('size', default_size)
    if margins: self.setMargins(**kwargs)
    self.setKeyOptions(kwargs.get('key', []))
    for axis in ['x', 'y']:
      self.setAxisLabel(kwargs.get(axis + 'label', ''), axis = axis)
      self.setAxisRange(kwargs.get(axis + 'r'), axis = axis)
    for k, v in kwargs.get('lines', {}).iteritems():
      axis, pos = k.split('=')
      if axis == 'y': self.setVerticalLine(float(pos), v)
      else: self.addHorizontalLine(float(pos), v)
    for k, v in kwargs.get('labels', {}).iteritems():
      self.setLabel(k, v[:2], v[-1])
    for a in kwargs.get('arrows', []): self.setArrow(*a)

  def _convert(self):
    """convert eps/ps original into pdf, png and jpg format"""
    pdf_dims = [
      int(ureg.parse_expression(s).to('point').magnitude)
      for s in self.size.split(',')
    ]
    call(' '.join([
      'gs', '-dBATCH', '-dNOPAUSE',
      '-sOutputFile=%s.pdf' % (self.name),
      '-sDEVICE=pdfwrite',
      '-dDEVICEWIDTHPOINTS=%d' % (pdf_dims[1]),
      '-dDEVICEHEIGHTPOINTS=%d' % (pdf_dims[0]),
      '-c "<</PageOffset [-50 -50]>> setpagedevice"',
      '-f', self.epsname
    ]), shell = True)
    for ext in ['.png', '.jpg']:
      call(' '.join([
        'convert -density 150', self.name + '.pdf', self.name + ext
      ]), shell = True)

  def _hdf5(self):
    """write data contained in plot to HDF5 file

    - easy numpy import -> (savetxt) -> gnuplot
    - export to ROOT objects

    h5py howto (see http://www.h5py.org/docs/intro/quick.html):
      - open file: `f = h5py.File(name, 'r')`
      - list datasets: `list(f)`
      - load entire dataset as np array: `arr = f['dset_name'][...]`
      - NOTE: literally type the 3 dots, replace dset_name
      - np.savetxt format: `fmt = '%.4f %.3e %.3e %.3e %.3e'`
      - save array to txt file: `np.savetxt('arr.dat', arr, fmt=fmt)`

    :raises: ImportError
    """
    try:
      import h5py
      f = h5py.File(self.name + '.hdf5', 'w')
      for k, v in self.dataSets.iteritems():
        f.create_dataset(k, data = v)
      f.close()
    except ImportError:
      print 'install h5py to also save an hdf5 file of your plot!'
    except:
      print 'h5py imported but error raised!'
      raise

  def _ascii(self):
    """write ascii file(s) w/ data contained in plot"""
    if not os.path.exists(self.name): os.makedirs(self.name)
    for k, v in self.dataSets.iteritems():
      np.savetxt(
        self.name + '/' + self._prettify(k) + '.dat', v, fmt='%.4e'
      )

  def _hardcopy(self):
    """generate eps, convert to other formats and write data to hdf5"""
    if self.nPanels < 1:
      #self.gp.hardcopy(
      #  self.epsname, enhanced = 1, color = 1, mode = 'landscape', fontsize = 24
      #)
      self._setter([
        'terminal postscript landscape enhanced color 24 size %s' % self.size,
        'output "%s"' % self.epsname,
      ])
      self.gp.refresh()
    self._convert()
    self._hdf5()
    self._ascii()

  def plot(self, hardcopy = True):
    """plot and generate output files"""
    self.gp.plot(*self.data)
    if hardcopy: self._hardcopy()
