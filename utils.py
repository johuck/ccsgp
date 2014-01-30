import itertools
from config import default_colors

def getOpts(i):
  """convience function for easy access to gnuplot property string"""
  return 'lt 1 lw 4 ps 2 lc %s pt 18' % default_colors[i]

def zip_flat(a, b, c=None):
  """zips two or three lists and flattens the result"""
  zipped = zip(a, b) if c is None else zip(a, b, c)
  return list(itertools.chain.from_iterable(zipped))
