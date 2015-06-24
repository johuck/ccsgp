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

def clamp(val, minimum = 0, maximum = 255):
  """convenience function to clamp number into min..max range"""
  if val < minimum: return minimum
  if val > maximum: return maximum
  return val

def colorscale(hexstr, scalefactor = 1.4):
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
  r = clamp(r * scalefactor)
  g = clamp(g * scalefactor)
  b = clamp(b * scalefactor)
  return 'rgb "#%02x%02x%02x"' % (r, g, b)
