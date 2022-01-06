# flake8: noqa: F401
import warnings

import numpy.distutils

# Workaround for theano bug that tries to access blas_opt_info
# https://github.com/pymc-devs/pymc/issues/5310
if (
    hasattr(numpy.distutils, '__config__') and
    numpy.distutils.__config__ and
    not hasattr(numpy.distutils.__config__, 'blas_opt_info')
):
    import numpy.distutils.system_info  # noqa

    # We need to catch warnings as in some cases NumPy print
    # stuff that we don't want the user to see.
    with warnings.catch_warnings(record=True):
        numpy.distutils.system_info.system_info.verbosity = 0
        blas_info = numpy.distutils.system_info.get_info('blas_opt')

    numpy.distutils.__config__.blas_opt_info = blas_info

from .model import (analyze_one,
                    analyze_two,
                    BestModel,
                    BestModelOne,
                    BestModelTwo,
                    BestResults,
                    BestResultsOne,
                    BestResultsTwo)
from .plot import (plot_all,
                   plot_all_one,
                   plot_all_two,
                   plot_posterior,
                   plot_data_and_prediction,
                   PRETTY_BLUE)
