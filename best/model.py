"""Bayesian estimation for two groups

This module implements Bayesian estimation for two groups, providing
complete distributions for effect size, group means and their
difference, standard deviations and their difference, and the
normality of the data.

Based on:

Kruschke, J. (2012) Bayesian estimation supersedes the t
    test. Journal of Experimental Psychology: General.

"""

from abc import ABC, abstractmethod
import sys

import arviz
import numpy as np
import pymc3 as pm
from pymc3.backends.base import MultiTrace
import scipy.stats as st


class BestModel(ABC):
    """Base class for BEST models"""

    @property
    @abstractmethod
    def version(self):
        """Version of the model specification

        For details, see the page :ref:`ch-model-history`.
        """
        pass

    @property
    @abstractmethod
    def model(self) -> pm.Model:
        """The underlying PyMC3 Model object

        (This property is accessible primarily for internal purposes.)
        """
        pass

    @abstractmethod
    def observed_data(self, group_id: int):
        """Return the observed data as a NumPy array

        (This method is accessible primarily for internal purposes.)
        """
        pass

    @abstractmethod
    def __str__(self):
        pass

    def sample(self, n_samples: int, **kwargs) -> MultiTrace:
        """Draw posterior samples from the model

        (This method is accessible primarily for internal purposes.)
        """

        kwargs['tune'] = kwargs.get('tune', 1000)
        pm_major, pm_minor, *_ = pm.__version__.split('.')
        if (int(pm_major), int(pm_minor)) < (3, 7):
            kwargs.setdefault('nuts_kwargs', {'target_accept': 0.90})
        else:
            kwargs.setdefault('target_accept', 0.9)
        max_rounds = 2
        for r in range(max_rounds):
            with self.model:
                trace = pm.sample(n_samples, **kwargs)

            if trace.report.ok:
                break
            else:
                if r == 0:
                    kwargs['tune'] = 2000
                    print('\nDue to potentially incorrect estimates, rerunning sampling '
                          'with {} tuning samples.\n'.format(kwargs['tune']), file=sys.stderr)
                else:
                    print('\nThe samples maybe are still not totally okay. '
                          'Try rerunning the analysis.')

        return trace


class BestModelOne(BestModel):
    """Model for a single-group analysis; subclass of :class:`BestModel`"""

    def __init__(self, y, ref_val):
        self.y = y = np.array(y)
        self.ref_val = ref_val

        assert y.ndim == 1

        self.mu_loc = mu_loc = np.mean(y)
        self.mu_scale = mu_scale = np.std(y) * 1000

        self.sigma_low = sigma_low = np.std(y) / 1000
        self.sigma_high = sigma_high = np.std(y) * 1000

        self.nu_min = nu_min = 2.5
        self.nu_mean = nu_mean = 30
        self._nu_param = nu_mean - nu_min

        with pm.Model() as self._model:
            mean = pm.Normal('Mean', mu=mu_loc, sd=mu_scale)
            logsigma = pm.Uniform('Log sigma', lower=np.log(sigma_low), upper=np.log(sigma_high))
            sigma = pm.Deterministic('Sigma', np.exp(logsigma))
            prec = sigma ** (-2)
            nu = pm.Exponential('nu - %g' % nu_min, 1 / (nu_mean - nu_min)) + nu_min
            _ = pm.Deterministic('Normality', nu)
            _ = pm.StudentT('Data', observed=y, nu=nu, mu=mean, lam=prec)
            stddev = pm.Deterministic('SD', sigma * (nu / (nu - 2)) ** 0.5)
            _ = pm.Deterministic('Effect size', (mean - ref_val) / stddev)

    @property
    def version(self):
        return 'v2'

    @property
    def model(self):
        return self._model

    def observed_data(self, group_id: int):
        if group_id == 1:
            return self.y
        else:
            raise ValueError('Group ID for a single-group analysis must be 1')

    def __repr__(self):
        return 'BestModelOne(y=%r, ref_val=%r, version=%r)' \
               % (self.y, self.ref_val, self.version)

    def __str__(self):
        return ('μ ~ Normal({0.mu_loc:.2e}, {0.mu_scale:.2e})\n'
                'log(σ) ~ Uniform(log({0.sigma_low:g}), log({0.sigma_high:g}))\n'
                'ν ~ Exponential(1/{0._nu_param:g}) + {0.nu_min:g}\n'
                'y ~ t(ν, μ, σ)\n'.format(self))


class BestModelTwo(BestModel):
    """Model for a two-group analysis; subclass of :class:`BestModel`"""

    def __init__(self, y1, y2):
        self.y1 = y1 = np.array(y1)
        self.y2 = y2 = np.array(y2)

        assert y1.ndim == 1
        assert y2.ndim == 1

        y_all = np.concatenate((y1, y2))

        self.mu_loc = mu_loc = np.mean(y_all)
        self.mu_scale = mu_scale = np.std(y_all) * 1000

        self.sigma_low = sigma_low = np.std(y_all) / 1000
        self.sigma_high = sigma_high = np.std(y_all) * 1000

        self.nu_min = nu_min = 2.5
        self.nu_mean = nu_mean = 30
        self._nu_param = nu_mean - nu_min

        with pm.Model() as self._model:
            # Note: the IDE might give a warning for these because it thinks
            #  distributions like pm.Normal() don't have a string "name" argument,
            #  but this is false – pm.Distribution redefined __new__, so the
            #  first argument indeed is the name (a string).
            group1_mean = pm.Normal('Group 1 mean', mu=mu_loc, sd=mu_scale)
            group2_mean = pm.Normal('Group 2 mean', mu=mu_loc, sd=mu_scale)

            nu = pm.Exponential('nu - %g' % nu_min, 1 / (nu_mean - nu_min)) + nu_min
            _ = pm.Deterministic('Normality', nu)

            group1_logsigma = pm.Uniform(
                'Group 1 log sigma', lower=np.log(sigma_low), upper=np.log(sigma_high)
            )
            group2_logsigma = pm.Uniform(
                'Group 2 log sigma', lower=np.log(sigma_low), upper=np.log(sigma_high)
            )
            group1_sigma = pm.Deterministic('Group 1 sigma', np.exp(group1_logsigma))
            group2_sigma = pm.Deterministic('Group 2 sigma', np.exp(group2_logsigma))

            lambda1 = group1_sigma ** (-2)
            lambda2 = group2_sigma ** (-2)

            group1_sd = pm.Deterministic('Group 1 SD', group1_sigma * (nu / (nu - 2)) ** 0.5)
            group2_sd = pm.Deterministic('Group 2 SD', group2_sigma * (nu / (nu - 2)) ** 0.5)

            _ = pm.StudentT('Group 1 data', observed=y1, nu=nu, mu=group1_mean, lam=lambda1)
            _ = pm.StudentT('Group 2 data', observed=y2, nu=nu, mu=group2_mean, lam=lambda2)

            diff_of_means = pm.Deterministic('Difference of means', group1_mean - group2_mean)
            _ = pm.Deterministic('Difference of SDs', group1_sd - group2_sd)
            _ = pm.Deterministic(
                'Effect size', diff_of_means / np.sqrt((group1_sd ** 2 + group2_sd ** 2) / 2)
            )

    @property
    def version(self):
        return 'v2'

    @property
    def model(self):
        return self._model

    def observed_data(self, group_id: int):
        if group_id == 1:
            return self.y1
        elif group_id == 2:
            return self.y2
        else:
            raise ValueError('Group ID for a two-group analysis must be 1 or 2')

    def __repr__(self):
        return 'BestModelTwo(y1=%r, y2=%r, version=%r)' \
               % (self.y1, self.y2, self.version)

    def __str__(self):
        return ('μ1 ~ Normal({0.mu_loc:g}, {0.mu_scale:g})\n'
                'μ2 ~ Normal({0.mu_loc:g}, {0.mu_scale:g})\n'
                'log(σ1) ~ Uniform(log({0.sigma_low:g}), log({0.sigma_high:g}))\n'
                'log(σ2) ~ Uniform(log({0.sigma_low:g}), log({0.sigma_high:g}))\n'
                'ν ~ Exponential(1/{0._nu_param:g}) + {0.nu_min:g}\n'
                'y1 ~ t(ν, μ1, σ1)\n'
                'y2 ~ t(ν, μ2, σ2)\n'.format(self))


class BestResults(ABC):
    """Results of an analysis"""
    def __init__(self, model: BestModel, trace: MultiTrace):
        self._model = model
        self._trace = trace

    @property
    def model(self):
        return self._model

    @property
    def trace(self) -> MultiTrace:
        """The collection of posterior samples

        See the relevant `PyMC3 documentation
        <https://docs.pymc.io/api/inference.html#multitrace>`_ for details.
        """
        return self._trace

    def observed_data(self, group_id: int):
        """Return the observed data as a NumPy array

        (This method is accessible primarily for internal purposes.)
        """
        return self.model.observed_data(group_id)

    def summary(self, credible_mass: float = 0.95):
        """Return summary statistics of the results

        Parameters
        ----------
        credible_mass : float
            The highest posterior density intervals in the summary will cover
            credible_mass * 100% of the probability mass.
            For example, credible_mass=0.95 results in 95% credible intervals.
            Default: 0.95.
        """
        return arviz.summary(self.trace, hdi_prob=credible_mass)

    def hdi(self, var_name: str, credible_mass: float = 0.95):
        """Calculate the highest posterior density interval (HDI)

        This function calculates a *credible interval* which contains the
        ``credible_mass`` most likely values of the parameter, given the data.
        Also known as an HPD interval.

        Parameters
        ----------
        var_name : str
            Name of variable.
        credible_mass : float
            The HDI will cover credible_mass * 100% of the probability mass.
            Default: 0.95, i.e. a 95% HDI.

        Returns
        -------
        (float, float)
            The endpoints of the HPD
        """
        az_major, az_minor, *_ = arviz.__version__.split('.')
        if (int(az_major), int(az_minor)) >= (0, 8):
            return tuple(arviz.hdi(self.trace[var_name], hdi_prob=credible_mass))
        else:
            return tuple(arviz.hpd(self.trace[var_name], credible_interval=credible_mass))

    def posterior_prob(self, var_name: str, low: float = -np.inf, high: float = np.inf):
        r"""Calculate the posterior probability that a variable is in a given interval

        The return value approximates the following probability:

        .. math:: \text{Pr}(\textit{low} < \theta_{\textit{var_name}} < \textit{high} | y_1, y_2)

        One-sided intervals can be specified by using only the ``low`` or ``high`` argument,
        for example, to calculate the probability that the the mean of the
        first group is larger than that of the second one::

            best_result.posterior_prob('Difference of means', low=0)

        Parameters
        ----------
        var_name : str
            Name of variable.
        low : float, optional
            Lower limit of the interval.
            Default: :math:`-\infty` (no lower limit)
        high : float, optional
            Upper limit of the interval.
            Default: :math:`\infty` (no upper limit)

        Returns
        -------
        float
            Posterior probability that the variable is in the given interval.

        Notes
        -----
        If *p* is the result and *S* is the total number of samples, then the
        standard deviation of the result is :math:`\sqrt{p(1-p)/S}`
        (see BDA3, p. 267). For example, with 2000 samples, the errors for
        some returned probabilities are

         - 0.01 ± 0.002,
         - 0.1 ± 0.007,
         - 0.2 ± 0.009,
         - 0.5 ± 0.011,

        meaning the answer is accurate for most practical purposes.
        """
        samples = self.trace[var_name]
        n_match = len(samples[(low < samples) * (samples < high)])
        n_all = len(samples)
        return n_match / n_all

    def posterior_mode(self,
                       var_name: str):
        """Calculate the posterior mode of a variable

        Parameters
        ----------
        var_name : string
            The name of the variable whose posterior mode is to be calculated.

        Returns
        -------
        float
            The posterior mode.
        """
        samples = self.trace[var_name]

        # calculate mode using kernel density estimate
        kernel = st.gaussian_kde(samples)

        bw = kernel.covariance_factor()
        cut = 3 * bw
        x_low = np.min(samples) - cut * bw
        x_high = np.max(samples) + cut * bw
        n = 512
        x = np.linspace(x_low, x_high, n)
        vals = kernel.evaluate(x)
        max_idx = np.argmax(vals)
        mode_val = x[max_idx]

        return mode_val


class BestResultsOne(BestResults):
    """Results of a two-group analysis; subclass of :class:`BestResults`"""

    def __init__(self, model: BestModelOne, trace: MultiTrace):
        super().__init__(model, trace)


class BestResultsTwo(BestResults):
    """Results of a two-group analysis; subclass of :class:`BestResults`"""

    def __init__(self, model: BestModelTwo, trace: MultiTrace):
        super().__init__(model, trace)

    def observed_data(self, group_id):
        return self.model.observed_data(group_id)


def analyze_two(group1_data,
                group2_data,
                n_samples: int = 2000,
                **kwargs) -> BestResultsTwo:
    """Analyze the difference between two groups

    This analysis takes about a minute, depending on the amount of data.
    (See the Notes section below.)

    This function creates a model with the given parameters, and updates the
    distributions of the parameters as dictated by the model and the data.

    Parameters
    ----------
    group1_data : list of numbers, NumPy array, or Pandas Series.
        Data of the first group analyzed and to be plotted.
    group2_data : list of numbers, NumPy array, or Pandas Series.
        Data of the second group analyzed and to be plotted.
    n_samples : int
        Number of samples *per chain* to be drawn for the analysis.
        (The number of chains depends on the number of CPU cores, but is
        at least 2.) Default: 2000.
    **kwargs
        Keyword arguments are passed to :meth:`pymc3.sample`.
        For example, number of tuning samples can be increased to 2000
        (from the default 1000) by::

            best.analyze_two(group1_data, group2_data, tune=2000)

    Returns
    -------
    BestResultsTwo
        An object that contains all the posterior samples from the model.

    Notes
    -----
    The first call of this function takes about 2 minutes extra, in order to
    compile the model and speed up later calls.

    Afterwards, performing a two-group analysis takes:
     - 20 seconds with 45 data points per group, or
     - 90 seconds with 10,000 data points per group.

    Don’t be taken aback by the time estimates in the beginning – the sampling
    process speeds up after the initial few hundred iterations.

    (These times were measured on a 2015 MacBook.)
    """
    model = BestModelTwo(group1_data, group2_data)
    trace = model.sample(n_samples, **kwargs)
    return BestResultsTwo(model, trace)


def analyze_one(group_data,
                ref_val: float = 0,
                n_samples: int = 2000,
                **kwargs) -> BestResultsOne:
    """Analyze the distribution of a single group

    This method is typically used to compare some observations against a
    reference value, such as zero. It can be used to analyze paired data,
    or data from an experiment without a control group.

    This analysis takes around a minute, depending on the amount of data.

    This function creates a model with the given parameters, and updates the
    distributions of the parameters as dictated by the model and the data.

    Parameters
    ----------
    group_data : list of numbers, NumPy array, or Pandas Series.
        Data of the group to be analyzed.
    ref_val : float
        The reference value to be compared against. This affects the plots
        and the effect size calculations. Default: 0.
    n_samples : int
        Number of samples *per chain* to be drawn for the analysis.
        (The number of chains depends on the number of CPU cores, but is
        at least 2.) Default: 2000.
    **kwargs
        Keyword arguments are passed to ``pymc3.sample``.
        For example, number of tuning samples can be increased to 2000
        (from the default 1000) by::

            best.analyze_one(group_data, tune=2000)

    Returns
    -------
    BestResultsOne
        An object that contains all the posterior samples from the model.

    Notes
    -----
    The first call of this function takes about 2 minutes extra, in order to
    compile the model and speed up later calls.

    Afterwards, performing a two-group analysis takes about 20 seconds on a
    2015 MacBook, both with 20 and 1000 data points.
    """

    model = BestModelOne(group_data, ref_val)
    trace = model.sample(n_samples, **kwargs)
    return BestResultsOne(model, trace)
