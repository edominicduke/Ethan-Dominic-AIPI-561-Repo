"""
Monitoring metrics skeleton.

This file defines 8 metric stubs for monitoring data and model health.
Implement at least 5 of the 8 metrics based on your monitoring framework design.
Each metric should compute a specific health signal about your data/model,
and return a dict (or float) that can be checked against your alert thresholds.
"""

import pandas as pd
import numpy as np
from scipy.stats import ks_2samp


class MetricComputer:
    """Compute monitoring metrics for drift detection."""

    def __init__(self, baseline_df: pd.DataFrame):
        """Initialize with baseline data."""
        self.baseline_df = baseline_df

    def metric_1_accuracy(
        self, new_df: pd.DataFrame, predictions: np.ndarray, actuals: np.ndarray
    ) -> float:
        """
        Metric 1: Overall Accuracy

        TODO: Implement. Return fraction of correct predictions.
        """
        num_correct_predictions = (np.abs(predictions - actuals) <= 0.2*actuals).sum()
        fraction_correct_predictions = num_correct_predictions/new_df.shape[0]

        return fraction_correct_predictions

    def metric_2_accuracy_by_zone(
        self, new_df: pd.DataFrame, predictions: np.ndarray, actuals: np.ndarray
    ) -> dict:
        """
        Metric 2: Accuracy by Zone

        TODO: Implement. Return dict mapping zone_id -> accuracy.
        """
        pass

    def metric_3_null_rates(self, new_df: pd.DataFrame) -> dict:
        """
        Metric 3: Null Rates for Critical Fields

        TODO: Implement. Return dict of field -> null_rate for critical columns.
        """
        null_rates = {}

        """
        The alert thresholds for PULocationID, trip_count, and the lag_features were listed BASELINE_METRICS.md. Therefore,
        the assumption is made that these are the only critical columns whose null rates need to be analyzed. However, I have
        additionally added the hour and dayofweek features since, as stated for the previous assignment, these are columns that
        cannot afford to have any null values.
        """
        critical_cols = ['PULocationID', 'hour', 'dayofweek', 'trip_count', 'lag_15min', 'lag_1h', 'lag_2h', 'lag_1day', 'lag_1week']
        for col in critical_cols:
            null_rates[col] = 100*new_df[col].isna().mean()
        return null_rates

    def metric_4_ks_test(self, new_df: pd.DataFrame) -> dict:
        """
        Metric 4: KS Test for Distribution Shift

        TODO: Implement. Use scipy.stats.ks_2samp to compare trip_count distribution.
        Return dict with statistic and p-value.
        """
        new_cutoff = pd.Timestamp("2026-02-02")
        feb_data = new_df[new_df["time_bucket"] >= new_cutoff]
        ks_2_test_results = ks_2samp(self.baseline_df["trip_count"], feb_data["trip_count"])
        statistic = ks_2_test_results.statistic
        p_value = ks_2_test_results.pvalue
        return (statistic, p_value)

    def metric_5_psi(self, new_df: pd.DataFrame, bins: int = 10) -> float:
        """
        Metric 5: Population Stability Index

        TODO: Implement PSI calculation. Compare baseline vs new distribution.
        Return single float value.
        """
        pass

    def metric_6_prediction_distribution(self, predictions: np.ndarray) -> dict:
        """
        Metric 6: Prediction Distribution Shift

        TODO: Implement. Check if model is collapsed (std very small).
        Return dict with mean, std, collapsed flag.
        """
        # Calculate the standard deviation of trip_count in the baseline data.
        trip_count_std_baseline = np.std(self.baseline_df["trip_count"].to_numpy())

        # Consider as collapsed if the standard deviation of trip_count in the predictions is < 0.25 * trip_count_std_baseline
        trip_count_std_pred = np.std(predictions)
        collapsed_flag = False
        if trip_count_std_pred < 0.25 * trip_count_std_baseline:
            collapsed_flag = True
        
        # Calculate the mean of the predictions.
        trip_count_mean_pred = np.mean(trip_count_std_baseline)

        return trip_count_mean_pred, trip_count_std_baseline, collapsed_flag, trip_count_std_baseline

    def metric_7_data_freshness(self, new_df: pd.DataFrame) -> dict:
        """
        Metric 7: Data Freshness

        TODO: Implement. Check age of most recent record.
        Return dict with age in minutes, hours.
        """
        pass

    def metric_8_duplicate_rate(self, new_df: pd.DataFrame) -> dict:
        """
        Metric 8: Duplicate Rate

        TODO: Implement. Check fraction of rows that are exact duplicates.
        Return dict with rate and count.
        """
        count_dup_rows = new_df.duplicated().sum()
        rate_dup_rows = 100*(count_dup_rows/new_df.shape[0])
        return (count_dup_rows, rate_dup_rows)

    def compute_all_metrics(
        self,
        new_df: pd.DataFrame,
        predictions: np.ndarray = None,
        actuals: np.ndarray = None,
    ) -> dict:
        """
        Compute all metrics.

        TODO: Call each metric method and return results dict.
        """

        # Initialize the results dictionary.
        results = {}

        # TODO: Populate results
        results["Overall_Accuracy"] = self.metric_1_accuracy(new_df, predictions, actuals)

        #results["Accuracy_by_Zone"] = self.metric_2_accuracy_by_zone(new_df, predictions, actuals)
        results["Null_Rates_for_Critical_Fields"] = self.metric_3_null_rates(new_df)

        results["KS_Test_for_Distribution_Shift"] = self.metric_4_ks_test(new_df)
        #results["Population_Stability_Index"] = self.metric_5_psi(new_df)
        results["Prediction_Distribution_Shift"] = self.metric_6_prediction_distribution(predictions)
        #results["Data_Freshness"] = self.metric_7_data_freshness(new_df)
        results["Duplicate_Rate"] = self.metric_8_duplicate_rate(new_df)

        # Return the results dictionary.
        return results
