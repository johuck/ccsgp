import itertools
from config import default_colors

def getOpts(i):
  """convience function for easy access to gnuplot property string"""
  return 'lt 1 lw 4 ps 2 lc %s pt 18' % default_colors[i]

def zip_flat(a, b):
  """zip two lists and flattens the result

  :returns: flatten list of elements in a & b alternately
  """
  return list(
    itertools.chain.from_iterable(zip(a, b))
  )
