"""

ccsgp_ is a plotting library based on gnuplot-py_ which wraps the necessary
calls to gnuplot-py into one function called ``make_plot``. The keyword
arguments to ``make_plot`` provide easy control over the plot-by-plot dependent
options while reasonable defaults for legend, grid, borders, font sizes,
terminal etc. are handled internally. By providing the data in a default and
reasonable format, the user does not need to deal with the details of
"gnuplot'ing" nor the internals of the gnuplot-py interface library.  Every call
of ``make_plot`` dumps an ascii representation of the plot in the terminal and
generates the eps hardcopy original. The eps figure is also converted
automatically into pdf, png and jpg formats for easy inclusion in presentations
and papers. In addition, the user can decide to save the data contained in each
image into hdf5 files for easy access via numpy. The function `repeat_plot`
allows the user replot a specific graph with different properties, like axis
ranges for instance. The ``make_panel`` user function facilitates plotting of
1D- or 2D-panel images with merged axes.

The name *ccsgp* stands for "Carbon Capture and Sequestration GnuPlot" as this
library started off in the context of my wife's research_.  I knew how to produce
nice-looking plots using gnuplot but wanted to hook it up to python directly.
The resulting library let's me generate identical plots independent of the data
input source (ROOT, YAML, txt, pickle, hdf5, ...) using the full power of
python.

.. _gnuplot-py: http://gnuplot-py.sourceforge.net/
.. _research: http://www.cchem.berkeley.edu/co2efrc/researchers/researchers/johanna-obst.html
"""
