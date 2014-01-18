import os, re, sys, logging
import Gnuplot, Gnuplot.funcutils
from subprocess import call
from utils import zip_flat
from config import basic_setup, default_margins, xPanProps

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
  :ivar axisLog: flags for logarithmic axes
  """
  def __init__(self, name = 'test', title = '', debug = 0):
    self.name = name
    self.epsname = name + '.eps'
    self.gp = Gnuplot.Gnuplot(debug = debug)
    self.nPanels = 0
    self.nVertLines = 0
    self.nLabels = 0
    self.axisLog = { 'x': False, 'y': False }
    self._setter(['title "%s"' % title] + basic_setup)

  def _using(self, data):
    """determine string with columns to use

    :param data: one dataset
    :type data: numpy.array
    :returns: '1:2:3', '1:2:4' or '1:2:3:4'
    """
    return ':'.join([
      '%d' % (i+1) for i in xrange(4)
      if i < 2 or (i >= 2 and self.error_sums[i-2] > 0)
    ])

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
      logging.critical(
        '%d columns not allowed, use either 2, 4 or 5!' % data.shape[1]
      )
      sys.exit(1)
    if data.shape[1] < 3: return False
    self.error_sums = [ self._sum_errs(data, i+2) for i in xrange(2) ]
    return (sum(self.error_sums) > 0)

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
    return '%serrorbars pt 0 lt 1 lc 0 lw %s' % (xy, lw)

  def _with_syserrs(self, prop):
    """generate special property string for secondary errors

    * draw box in same color as point/line color

    :param prop: property string of a dataset
    :type prop: str
    :returns: property string for secondary errors
    """
    m_lw = re.compile('lw \d').search(prop)
    lw = m_lw.group()[-1] if m_lw else '1'
    m_lc = re.compile('lc \d').search(prop)
    if not m_lc:
      m_lc = re.compile('lc rgb "#[A-Fa-f0-9]{6}"').search(prop)
    return 'candlesticks fs solid lw %s lt 1 %s' % (
      lw, m_lc.group() if m_lc else 'lc 0'
    )

  def initData(self, data, properties, titles):
    """initialize the data

    - all lists given as parameters must have the same length.
    - each data set is drawn twice to allow for different colors for the errorbars
    - error bars use the same linewidth as data points and line color black

    :param data: data points w/ format [x, y, dx, dy] for each dataset
    :type data: list of numpy arrays
    :param properties: plot properties for each dataset (pt/lw/ps/lc...)
    :type properties: list of str
    :param titles: key/legend titles for each dataset
    :type titles: list of strings
    :var dataSets: zipped titles and data for hdf5 output and setAxisRange
    :var data: list of Gnuplot.Data including extra data sets for error plotting
    """
    # dataSets used in hdf5() and setAxisRange
    self.dataSets = dict( (k, v) for k, v in zip(titles, data) if k )
    # zip all input parameters for easier looping
    zipped = zip(data, properties, titles)
    # main data points drawn last
    main_data = [
      Gnuplot.Data(# TODO: linespoints?
        d, inline = 1, title = t, using = '1:2', with_ = ' '.join(['points', p])
      ) for d, p, t in zipped
    ]
    # extra data set to plot "primary" errors separately
    prim_errs = [
      Gnuplot.Data(
        d, inline = 1, using = self._using(d), with_ = self._with_errs(d, p)
      ) if self._plot_errs(d) else None
      for d, p, t in zipped
    ]
    # extra data set for "secondary" errors (systematic uncertainties)
    # TODO: automatically set boxwidth (relative to point width?)
    self.gp('set boxwidth 0.03 absolute')
    sec_errs = [
      Gnuplot.Data(
        d, inline = 1, using = '1:($2-$5):2:2:($2+$5)',
        with_ = self._with_syserrs(p)
      ) if self._sum_errs(d, 4) > 0 else None
      for d, p, t in zipped
    ]
    # zip main & secondary data and filter out None's
    # TODO: extend to more than two lists
    self.data = filter(None, zip_flat(sec_errs, prim_errs, main_data))

  def _setter(self, list):
    """convenience function to set a list of gnuplot options

    :param list: list of strings given to gnuplot's set command
    :type list: list
    """
    for s in list: self.gp('set %s' % s)

  def setMargins(self, **kwargs):
    """set the margins
    
    keys other than l(b,t,r)margin are ignored (see config.default_margins)
    """
    self._setter([
      '%s %f' % (k, kwargs.get(k, default_margins[k]))
      for k in default_margins
    ])

  def setKeyOptions(self, key_opts):
    """set key options

    :param key_opts: strings for key/legend options
    :type key_opts: list
    """
    self._setter(['key %s' % s for s in key_opts])

  def setAxisRange(self, rng, axis = 'x'):
    """set range for specified axis

    automatically determines axis range to include all data points if range is
    not given.

    :param rng: lower and upper range limits
    :type rng: list
    :param axis: axis to which to apply range
    :type axis: str
    """
    if rng is None:
      col = int(axis == 'y')
      vals = [ n for v in self.dataSets.values() for n in v[:, col] ]
      axMin, axMax = min(vals), max(vals)
      add_rng = 0.1 * (axMax - axMin)
      rng = [
        axMin - add_rng if not self.axisLog[axis] else 0.9 * axMin,
        axMax + add_rng if not self.axisLog[axis] else 1.1 * axMax,
      ]
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

  def prepare_plot(self, **kwargs):
    """prepare for plotting (calls all members of MyPlot)"""
    self.setMargins(**kwargs)
    self.setKeyOptions(kwargs.get('key', []))
    for axis in ['x', 'y']:
      self.setAxisLabel(kwargs.get(axis + 'label', ''), axis = axis)
      self.setAxisLog(kwargs.get(axis + 'log'), axis = axis)
      self.setAxisRange(kwargs.get(axis + 'r'), axis = axis)
    for k, v in kwargs.get('vert_lines', {}).iteritems():
      self.setVerticalLine(float(k), v)
    for k, v in kwargs.get('labels', {}).iteritems():
      self.setLabel(k, v[:2], v[-1])

  def _convert(self):
    """convert eps original into pdf, png and jpg format"""
    call(' '.join([
      'ps2pdf -dEPSCrop', self.epsname, self.name + '.pdf'
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
      - load entire dataset as np array: `arr = f['dst_name'][...]`
      - NOTE: literally type the 3 dots, replace dset_name
      - np.savetxt format: `fmt = '%.4f %.3e %.3e %.3e'`
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

  def _hardcopy(self):
    """generate eps, convert to other formats and write data to hdf5"""
    self.gp.hardcopy(
      self.epsname, enhanced = 1, color = 1, mode = 'landscape', fontsize = 24
    )
    self._convert()
    self._hdf5()

  def plot(self):
    """plot and generate output files"""
    self.gp.plot(*self.data)
    if self.nPanels < 1: self._hardcopy()


########################################################
## TODO: below are needed for multiplot and under dev ##
########################################################
#  def prepare_multiplot(self):
#    panel_setup = [
#      'terminal postscript eps enhanced color "Helvetica" 24',
#      'size %f,1' % xPanProps[0], 'output "%s"' % plt.epsname,
#      'multiplot'
#    ]
#    self._setter(panel_setup)
#
#  def prepare_subfig(self):
#    pan_wdth = xPanProps[1] * xPanProps[0]
#    xorig = xPanProps[2] + self.nPanels * pan_wdth
#    self.gp('set origin %f,0' % xorig)
#    self.gp('set size %f,1' % pan_wdth)
#    if self.nPanels > 0: self.gp('set ytics format " "')
#    self.nPanels += 1
#
########################################################
