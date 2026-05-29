"""
Data Quality Validation Tests Template

Write tests that:
1. Pass for clean (baseline) data
2. Fail for corrupted data
3. Test each issue you identified
"""

import pytest
import pandas as pd
import numpy as np
import logging

# TODO: Import your validation class
from validation.check_data_quality import DataQualityValidator
from backend.data import *


@pytest.fixture
def baseline_data():
    """Load clean baseline data."""
    # TODO: Load your clean baseline dataframe.
    CUTOFF = pd.Timestamp("2026-01-16")
    df = pd.read_parquet('week3/data/demand_enriched_corrupted.parquet')
    baseline = df[df['time_bucket'] < CUTOFF]   # clean historical window
    return baseline


@pytest.fixture
def corrupted_data():
    """Load corrupted data."""
    # TODO: Load your corrupted dataframe.
    CUTOFF = pd.Timestamp("2026-01-16")
    df = pd.read_parquet('week3/data/demand_enriched_corrupted.parquet')
    corrupted = df[df['time_bucket'] >= CUTOFF]  # new potentially corrupted window
    return corrupted


@pytest.fixture
def validator(baseline_data):
    """Create validator initialized with baseline."""
    # TODO: Create DataQualityValidator(baseline_data)
    return DataQualityValidator(baseline_data)


# ============================================================================
# TEST STRUCTURE EXAMPLES
# ============================================================================


class TestBaselineData:
    """Tests that baseline data should pass validation."""

    def test_baseline_passes_validation(self, baseline_data, validator):
        """Baseline data should have no quality issues."""
        # TODO: Implement
        result = validator.validate(baseline_data)
        assert result['is_valid'], f"Baseline failed: {result['issues']}"


class TestDataQualityIssues:
    """Tests that verify each issue is detected."""

    # The first issue we will be detecting is the duplicates that exist in the corrupted data.
    def test_detect_issue_1(self, corrupted_data, validator):
        """Should detect Issue 1 (TODO: describe your issue)."""
        # TODO: Implement
        result = validator.validate(corrupted_data)
        assert not result['is_valid']
        assert any(issue['type'] == "There are duplicates present in the dataset" for issue in result['issues'])
    
    # The second issue we will be detecting is differing distributions between the baseline data and the corrupted data.
    def test_detect_issue_2(self, corrupted_data, validator):
        """Should detect Issue 2 (TODO: describe your issue)."""
        # TODO: Implement
        result = validator.validate(corrupted_data)
        assert not result['is_valid']
        assert any(issue['type'] == "There are percentage differences between the feature means of the corrupted data and the baseline data" for issue in result['issues'])
        assert any(issue['type'] == "There are percentage differences between the feature standard deviations of the corrupted data and the baseline data" for issue in result['issues'])

    # It's recommended but optional to find all 4 issues:
    # def test_detect_issue_3(self, corrupted_data, validator):
    #     """Should detect Issue 3 (TODO: describe your issue)."""
    #     # TODO: Implement
    #     pass

    # def test_detect_issue_4(self, corrupted_data, validator):
    #     """Should detect Issue 4 (TODO: describe your issue)."""
    #     # TODO: Implement
    #     pass


class TestGracefulDegradation:
    """Tests that API gracefully handles bad data."""

    def test_api_does_not_crash_with_bad_data(self, corrupted_data):
        """API should continue running even with corrupted data."""
        # TODO: Test that your data.py doesn't crash
        # - Try to make predictions
        #for i in range(corrupted_data.shape[0]):

        num_heatmap_predictions_none = 0
        num_forecast_predictions_none = 0
        num_recommendation_predictions_none = 0

        for i in range(0, 30, 10):
            data_point = corrupted_data.iloc[i]
            heatmap_prediction = get_heatmap(data_point["hour"], data_point["dayofweek"])
            forecast_prediction = forecast_demand(data_point["PULocationID"], data_point["hour"], data_point["dayofweek"])
            recommendation_prediction = get_recommendations(data_point["PULocationID"], data_point["hour"], data_point["dayofweek"])

            # - Verify API returns something (even if degraded)
            if heatmap_prediction is None:
                num_heatmap_predictions_none += 1
            if forecast_prediction is None:
                num_forecast_predictions_none += 1
            if recommendation_prediction is None:
                num_recommendation_predictions_none += 1
        
        assert num_heatmap_predictions_none == 0 and num_forecast_predictions_none == 0 and num_recommendation_predictions_none == 0

    def test_fallback_is_logged(self, corrupted_data, caplog):
        """When graceful degradation happens, it should be logged."""
        # TODO: Test logging
        # - Run with corrupted data        
        # - Check logs show what degraded
        caplog.set_level(logging.WARNING)
        check_and_log_data_quality()
        assert caplog.records


# ============================================================================
# HOW TO RUN
# ============================================================================
#
# From repo root:
#   python -m pytest week3/validation/test_data_quality.py -v
#
# To run specific test:
#   python -m pytest week3/validation/test_data_quality.py::TestDataQualityIssues::test_detect_issue_1 -v
#
# To see print statements:
#   python -m pytest week3/validation/test_data_quality.py -v -s