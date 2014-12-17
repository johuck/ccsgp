"""
:var default_key: default options for legend/key
:var basic_setup: bars, grid, terminal and default_key
:var default_margins: default margins to define plot area
:var xPanProps: xscale, xsize, xoffset for panel plots
:var default_colors: provides a reasonable color selection (see palette_)

.. _palette: http://colorbrewer2.org/
"""

default_size = '7in,10in'

default_key = [
  'spacing 1.2', 'samplen 1.5', 'reverse Left',
  'box lw 2', 'height 0.5', 'font ",22"'
]

basic_setup = [
  'grid lt 4 lc rgb "#C8C8C8"', 'terminal dumb'
] + [
  'key %s' % s for s in default_key
]

# TODO: boxerrorbars
supported_styles = [ '', 'points', 'lines', 'linespoints', 'filledcurves' ]

default_colors = [
  # http://colorbrewer2.org/?type=qualitative&scheme=Set1&n=9
  'rgb "#e41a1c"', 'rgb "#377eb8"', 'rgb "#4daf4a"',
  'rgb "#984ea3"', 'rgb "#ff7f00"', 'rgb "#ffff33"',
  'rgb "#a65628"', 'rgb "#f781bf"', 'rgb "#999999"',
  # http://colorbrewer2.org/?type=qualitative&scheme=Paired&n=9
  'rgb "#a6cee3"', 'rgb "#1f78b4"', 'rgb "#b2df8a"',
  'rgb "#33a02c"', 'rgb "#fb9a99"', 'rgb "#e31a1c"',
  'rgb "#fdbf6f"', 'rgb "#ff7f00"', 'rgb "#cab2d6"',
  # Johanna Huck
  'rgb "#ff8c00"', 'rgb "#228b22"', 'rgb "#b22222"',
  'rgb "#9370db"', 'rgb "#bdb76b"', 'rgb "#00bfff"',
  'rgb "#fa8072"', 'rgb "#ee82ee"', 'rgb "#7fffd4"',
  'rgb "#0000cd"', 'rgb "#ffdab9"', 'rgb "#eee9e9"',
  'rgb "#eecbad"', 'rgb "#a0522d"', 'rgb "#2e8b57"',
  'rgb "#3cb371"', 'rgb "#20b2aa"', 'rgb "#98fb98"',
  'rgb "#db7093"', 'rgb "#b03060"', 'rgb "#c71585"',
  'rgb "#bc8f8f"', 'rgb "#cd5c5c"',
  # http://stackoverflow.com/questions/17120363/default-colour-set-on-gnuplot-website
  'rgb "#ff0000"', 'rgb "#009e73"', 'rgb "#56b4e9"',
  'rgb "#e69f00"', 'rgb "#f0e442"', 'rgb "#0072b2"',
  'rgb "#e51e10"', 'rgb "#000000"', 'rgb "#7f7f7f"',
  # grayscale
  'rgb "#eeeeee"', 'rgb "#dddddd"', 'rgb "#cccccc"',
  'rgb "#bbbbbb"', 'rgb "#aaaaaa"', 'rgb "#999999"',
  'rgb "#888888"', 'rgb "#777777"', 'rgb "#666666"',
  'rgb "#555555"', 'rgb "#444444"', 'rgb "#333333"',
  'rgb "#222222"', 'rgb "#111111"', 'rgb "#000000"',
]

from pint import UnitRegistry
ureg = UnitRegistry()
