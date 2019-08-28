import pickle
import os

import numpy as np
import pytest

import best

@pytest.fixture
def data_dir():
    dir_path = os.path.join('tests', 'data')

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    return dir_path


def test_plot_all_one(data_dir):
    # data was generated by:
    # >>> np.random.seed(0)
    # >>> diff = st.t(df=20, loc=0.5, scale=0.2).rvs(20)
    # >>> morning = st.norm(loc=9, scale=0.5).rvs(20)  # doesn't matter at all
    # >>> evening = morning + diff
    morning = [8.99, 9.21, 9.03, 9.15, 8.68, 8.82, 8.66, 8.82, 8.59, 8.14, 9.09, 8.80, 8.18, 9.23, 8.55, 9.03, 9.36,
               9.06, 9.57, 8.38]
    evening = [9.82, 9.34, 9.73, 9.93, 9.33, 9.41, 9.48, 9.14, 8.62, 8.60, 9.60, 9.41, 8.43, 9.77, 8.96, 9.81, 9.75,
               9.50, 9.90, 9.13]

    filename = os.path.join(data_dir, 'results_one.bin')

    try:
        with open(filename, "rb") as f:
            best_out = pickle.load(f)
            print('Previous analysis loaded from "%s"' % filename)

    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        print("Performing Bayesian analysis")
        best_out = best.analyze_one(np.subtract(evening, morning))

        print('Saving results to "%s"' % filename)
        with open(filename, "wb") as f:
            pickle.dump(best_out, f)

    # Check that plotting doesn’t raise any exceptions
    fig = best.plot_all(best_out)
    fig.savefig(os.path.join(data_dir, 'plot_all_one.pdf'))


def test_plot_all_two(data_dir):
    drug = [101, 100, 102, 104, 102, 97, 105, 105, 98, 101, 100, 123, 105,
            103, 100, 95, 102, 106, 109, 102, 82, 102, 100, 102, 102, 101,
            102, 102, 103, 103, 97, 97, 103, 101, 97, 104, 96, 103, 124,
            101, 101, 100, 101, 101, 104, 100, 101]
    placebo = [99, 101, 100, 101, 102, 100, 97, 101, 104, 101, 102, 102,
               100, 105, 88, 101, 100, 104, 100, 100, 100, 101, 102, 103,
               97, 101, 101, 100, 101, 99, 101, 100, 100, 101, 100, 99,
               101, 100, 102, 99, 100, 99]

    filename = os.path.join(data_dir, 'results_two.bin')

    try:
        with open(filename, "rb") as f:
            best_out = pickle.load(f)
            print('Previous analysis loaded from "%s"' % filename)

    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        print("Performing Bayesian analysis")
        best_out = best.analyze_two(drug, placebo)

        print('Saving results to "%s"' % filename)
        with open(filename, "wb") as f:
            pickle.dump(best_out, f)

    # Check that plotting doesn’t raise any exceptions
    fig = best.plot_all(best_out)
    fig.savefig(os.path.join(data_dir, 'plot_all_two.pdf'))
