"""
.. module:: config
   :platform: Unix, Windows
   :synopsis: defines config variables for ccsgp

.. moduleauthor:: Patrick Huck <phuck@lbl.gov>

:var default_key: default options for legend/key
:var basic_setup: bars, grid, terminal and default_key
:var default_margins: default margins to define plot area
:var xPanProps: xscale, xsize, xoffset for panel plots
:var default_colors: provides a reasonable color selection (up to 31)
"""

default_key = [
  'spacing 1.2', 'samplen 1.5', 'reverse Left',
  'box lw 2', 'height 0.5', 'font ",22"'
]

basic_setup = [
  'bars small', 'grid lt 4 lc rgb "#C8C8C8"', 'terminal dumb'
] + [
  'key %s' % s for s in default_key
]

default_margins = { 'l': 5, 'b': 1, 'r': 0.1, 't': 0.1 }

xPanProps = [ 1.9, 0.23, 0.15 ]

default_colors = [
  '0', '1', '2', '3', '4', '5', '6', '9',
  'rgb "#ff8c00"', 'rgb "#228b22"', 'rgb "#b22222"',
  'rgb "#9370db"', 'rgb "#bdb76b"', 'rgb "#00bfff"',
  'rgb "#fa8072"', 'rgb "#ee82ee"', 'rgb "#7fffd4"',
  'rgb "#0000cd"', 'rgb "#ffdab9"', 'rgb "#eee9e9"',
  'rgb "#eecbad"', 'rgb "#a0522d"', 'rgb "#2e8b57"',
  'rgb "#3cb371"', 'rgb "#20b2aa"', 'rgb "#98fb98"',
  'rgb "#db7093"', 'rgb "#b03060"', 'rgb "#c71585"',
  'rgb "#bc8f8f"', 'rgb "#cd5c5c"'
]
