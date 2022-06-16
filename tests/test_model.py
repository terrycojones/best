import numpy as np
import pytest

import best

DUMMY_VAR_NAME = 'Means'


@pytest.fixture
def mock_trace():
    np.random.seed(0)
    S = 10000
    return best.model.BestResultsOne(None, {DUMMY_VAR_NAME: np.random.randn(S)}), S


def test_posterior_prob(mock_trace):
    br, S = mock_trace

    def error(p):
        return (p * (1 - p) / S) ** 0.5 * 3

    assert br.posterior_prob(DUMMY_VAR_NAME, -1, 1) == pytest.approx(0.683, abs=error(0.683))
    assert br.posterior_prob(DUMMY_VAR_NAME, low=1) == pytest.approx(0.159, abs=error(0.159))
    assert br.posterior_prob(DUMMY_VAR_NAME, high=-1) == pytest.approx(0.159, abs=error(0.159))
    assert br.posterior_prob(DUMMY_VAR_NAME, low=1, high=-1) == 0
    assert br.posterior_prob(DUMMY_VAR_NAME) == 1


def test_hdi_ok(mock_trace):
    br, _ = mock_trace
    assert br.hdi(DUMMY_VAR_NAME, 0.95) == pytest.approx((-1.96, 1.96), abs=0.1)


@pytest.mark.parametrize("credible_mass", [0, 1.01])
def test_valueerror(mock_trace, credible_mass):
    br, _ = mock_trace
    with pytest.raises(ValueError):
        br.hdi(DUMMY_VAR_NAME, credible_mass=credible_mass)

    with pytest.raises(ValueError):
        br.summary(credible_mass=credible_mass)
