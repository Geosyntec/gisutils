import sys
import matplotlib
matplotlib.use('agg')

import gisutils
status = gisutils.test(*sys.argv[1:])
sys.exit(status)
