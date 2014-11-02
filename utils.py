import itertools
from config import default_colors

def getOpts(i):
  """convience function for easy access to gnuplot property string"""
  nr_colors = len(default_colors)
  if i >= nr_colors: i = i%nr_colors # avoid index out of range error
  return 'lt 1 lw 4 ps 2 lc %s pt 18' % default_colors[i]

def zip_flat(a, b, c=None, d=None):
  """zips 2-4 lists and flattens the result"""
  if c is None and d is None:
      zipped = zip(a, b)
  elif d is None:
      zipped = zip(a, b, c)
  else:
      zipped = zip(a, b, c, d)
  return list(itertools.chain.from_iterable(zipped))
