BEST: Bayesian Estimation Supersedes the t-test
========================================================

*Bayesian parameter estimation, made simple.*

BEST is a tool to replace t-tests with Bayesian estimation,
and it can create beautiful plots and simple summaries in just a few lines of Python code::

    >>> group1_data = [101, 100, 102, 104, 102,  # ...
    ...                101, 101, 104, 100, 101]
    >>> group2_data = [102, 100,  97, 101, 104,  # ...
    ...                100, 101, 100, 102, 99, 100, 99]
    >>> best_out = best.analyze_two(group1_data, group2_data)
    >>> fig = best.plot_all(best_out)
    >>> fig.savefig('best_plots.pdf')

.. image:: ../examples/smart_drug.png
    :align: center
    :alt: Output of best.plot_all().

BEST gives intuitive results without being a statistician.
For example, to find the probability that the first group's mean is larger by at least 0.5 than the other's::

   >>> best_out.posterior_prob('Difference of means', low=0.5)
   0.87425

The 95% highest posterior density interval (HDI) can be queried just as easily::

    >>> best_out.hdi('Difference of means', 0.95)
    (0.12..., 1.84...)

The parameter estimation is described briefly in :ref:`the relevant section <brief-description>` of this documentation,
or in detail in the following publication:

   Kruschke, J. K. (2013). Bayesian estimation supersedes the *t* test.
   *Journal of Experimental Psychology: General* **142(2)**, pp.573-603.
   (doi: `10.1037/a0029146 <https://dx.doi.org/10.1037/a0029146>`_)

The publication's `accompanying website <http://www.indiana.edu/~kruschke/BEST/>`_
points to more resources on the topic.

Purpose
-------

BEST is intended as a replacement for a t-test,
to help transition to a world where science embraces uncertainty,
while keeping the tools simple.

It is *not* intended as a comprehensive data analysis tool.
For that purpose, please refer to books like John K. Kruschke's
`Doing Bayesian Data Analysis <https://sites.google.com/site/doingbayesiandataanalysis/>`_.
Quote from chapter 1 of the book:

    This book explains how to actually do Bayesian data analysis, by real people (like
    you), for realistic data (like yours). The book starts at the basics, with elementary
    notions of probability and programming. You do not need to already know statistics
    and programming.

The following open access papers give an intuitive introduction to Bayesian data analysis:

 - Kruschke, J. K. and Liddell, T. M. (2018).
    The Bayesian New Statistics: Hypothesis testing, estimation, meta-analysis, and power analysis from a Bayesian perspective.
    *Psychonomic Bulletin & Review* **25**, pp. 178-206.
    `R code <https://osf.io/j6364/files/>`_;
    see also the `Shiny App <http://www.indiana.edu/~kruschke/bayesAndFreqApp.html>`_.
    (doi: `10.3758/s13423-016-1221-4 <https://doi.org/10.3758/s13423-016-1221-4>`_)
 -  Kruschke, J. K. and Liddell, T. M. (2018).
    Bayesian data analysis for newcomers.
    *Psychonomic Bulletin & Review* **25**, pp. 155-177.
    (doi: `10.3758/s13423-017-1272-1 <https://doi.org/10.3758/s13423-017-1272-1>`_)

Installation
------------

The ``best`` package requires Python 3.5.4 or higher,
and can be installed with *pip*:

.. code-block:: bash

   pip install best

This command installs the following dependencies:

 - `SciPy <https://scipy.org/>`_,
 - `Matplotlib <http://matplotlib.org>`_ (≧ 3.0.0),
 - `PyMC3 <https://github.com/pymc-devs/pymc>`_.

Get in touch
------------

If you find the documentation lacking or you have found an error,
please `open an issue <https://github.com/treszkai/best/issues>`_  at the project's GitHub page,
or open a `pull request <https://github.com/treszkai/best/pulls>`_ if you have a proposed solution.

Your feedback and contribution are welcome!

Further documentation
---------------------

.. toctree::
    :maxdepth: 2

    api
    explanations
    model_history
    version_history