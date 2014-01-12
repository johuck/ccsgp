"""
.. module:: config
   :platform: Unix, Windows
   :synopsis: defines config variables for ccsgp

.. moduleauthor:: Patrick Huck <phuck@lbl.gov>
"""

default_key = [
  'spacing 1.4', 'samplen 2.2', 'reverse Left',
  'box lw 2', 'height 0.5', 'font ",22"'
]

basic_setup = [
  'bars small', 'grid lt 4 lc rgb "#C8C8C8"', 'terminal dumb'
] + [
  'key %s' % s for s in default_key
]

default_margins = { 'l': 5, 'b': 1, 'r': 0.1, 't': 0.1 }

# xscale, xsize, xoffset for panel plots
xPanProps = [ 1.9, 0.23, 0.15 ]
