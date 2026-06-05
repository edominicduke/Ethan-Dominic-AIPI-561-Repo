import pytest
import pandas as pd
import numpy as np
from metric_template import *
from detect_drift import *

"""
Run with pytest week4/scripts/test_monitoring.py.
"""

@pytest.fixture
def baseline_data():
    return pd.read_parquet("week4/data/demand_enriched_baseline.parquet")

@pytest.fixture
def new_data():
    return pd.read_parquet("week4/data/demand_enriched_week4.parquet")

@pytest.fixture
def metric_computer(baseline_data):
    return MetricComputer(baseline_data)

@pytest.fixture
def actuals(new_data):
    return new_data["trip_count"].values

@pytest.fixture
def ones_arr(actuals):
    return np.ones(actuals.shape)

def test_metric_1_accuracy(metric_computer, new_data, actuals):
    assert metric_computer.metric_1_accuracy(new_data, actuals, actuals) == 1.0

def test_metric_3_null_rates(metric_computer, baseline_data):
    assert max(metric_computer.metric_3_null_rates(baseline_data).values()) == 0.0

def test_metric_4_ks_test(metric_computer, new_data):
    assert metric_computer.metric_4_ks_test(new_data)[1] < 0.05

def test_metric_6_prediction_distribution(metric_computer, actuals, ones_arr):
    assert metric_computer.metric_6_prediction_distribution(actuals)[2] == False
    assert metric_computer.metric_6_prediction_distribution(ones_arr)[2] == True

def test_metric_8_duplicate_rate(metric_computer, baseline_data):
    assert metric_computer.metric_8_duplicate_rate(baseline_data)[1] == 0.0