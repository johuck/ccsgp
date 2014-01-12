""" library providing wrapper functions to gnuplot-py

.. moduleauthor:: Patrick Huck <phuck@lbl.gov>

ccsgp [1] is a plotting library based on gnuplot-py [2,3] which wraps the
necessary calls to gnuplot-py into one function called 'make_plot'. The keyword
arguments to 'make_plot' provide easy control over the plot-by-plot dependent
options while reasonable defaults for legend, grid, borders, font sizes,
terminal etc. are handle internally. By providing the data in a default and
reasonable format, the user does not need to deal with the details of
"gnuplot'ing" nor the internals of the gnuplot-py interface library.  Every call
of 'make_plot' dumps an ascii representation of the plot in the terminal and
generates the eps hardcopy original. The eps figure is also converted
automatically into pdf, png and jpg format for easy inclusion in presentations
and papers. In addition, the user can decide to save the data contained in each
image into hdf5 files for easy access via numpy. See
$ pydoc pyana.ccsgp.make_plot
for more details on the keyword options to 'make_plot'.

repeat_plot to replot with different axis ranges for instance.
make_panel for panel plots (under construction)

The name *ccsgp* stands for "Carbon Capture and Sequestration GnuPlot" as this
library has first been developed in the context of the research of Johanna Huck.
I knew how to produce nice-looking plots using gnuplot but wanted to hook it up
to python directly. Now I can generate identical plots independent of the data
input source (ROOT, YAML, txt, pickle, hdf5, ...).

[1] http://gitlab.the-huck.com/ccs-pe-eval/ccsgp
[2] http://gnuplot-py.sourceforge.net/
[3] http://www.youtube.com/watch?v=b_y_cLX526c
"""
