"""
Drift detection skeleton.

Write code to detect 4+ distinct drift patterns between baseline and new data.
Use statistical tests (KS, PSI, chi-square) to quantify drift.
"""

import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
from metric_template import *
from compute_metrics import *
from pathlib import Path
import lightgbm as lgb

_ROOT = Path(__file__).parent.parent.parent
MODEL_PATH = _ROOT / "week2" / "model" / "lgbm_demand_model.txt"

def load_data():
    # Load and return the baseline data and the new data.
    baseline = pd.read_parquet("week4/data/demand_enriched_baseline.parquet")
    new_data = pd.read_parquet("week4/data/demand_enriched_week4.parquet")
    return baseline, new_data

def detect_feature_drift(baseline_df: pd.DataFrame, new_df: pd.DataFrame) -> dict:
    """
    Detect drift in a the specified features in BASELINE_METRICS.md.

    TODO: Use KS test to compare baseline vs new distribution.
    Return dict with test results and interpretation.
    """
    test_results_with_interpretations = {}

    new_cutoff = pd.Timestamp("2026-02-02")
    feb_data = new_df[new_df["time_bucket"] >= new_cutoff]

    metrics_list = ["trip_count", "hour", "dayofweek"]

    for metric in metrics_list:
        ks_2_results_for_metric = ks_2samp(baseline_df[metric], feb_data[metric])
        ks_2_pvalue_for_metric = ks_2_results_for_metric.pvalue
        metric_interpretation = ""
        if ks_2_pvalue_for_metric > 0.05:
            metric_interpretation = f"Healthy: the baseline distribution for {metric} and the new distribution for {metric} is not significantly different."
        elif 0.01 < ks_2_pvalue_for_metric <= 0.05:
            metric_interpretation = f"Warning: the baseline distribution for {metric} and the new distribution for {metric} is significantly different."
        elif ks_2_pvalue_for_metric < 0.01:
            metric_interpretation = f"Critical: there is significant drift for {metric}. The baseline distribution for {metric} and the new distribution for {metric} is significantly different."

        test_results_with_interpretations[metric] = (ks_2_pvalue_for_metric, metric_interpretation)

    return test_results_with_interpretations


def detect_concept_drift_by_segment(baseline_df: pd.DataFrame, new_df: pd.DataFrame) -> dict:
    """
    Detect concept drift (accuracy degradation by segment).

    TODO: Compare mean/accuracy by zone/hour between baseline and new data.
    Find segments where performance dropped.
    Return dict with findings.
    """
    findings_mean = {}
    findings_acc = {}

    baseline_df_copy = baseline_df.copy()
    new_df_copy = new_df.copy()

    new_cutoff = pd.Timestamp("2026-02-02")
    feb_data = new_df_copy[new_df_copy["time_bucket"] >= new_cutoff]
    metrics_to_segment_by = ["PULocationID", "hour", "dayofweek"]

    # Get the predicted number of pickups for each zone for both the baseline data and the new data.
    predictions_baseline = pd.Series(data=get_pred_num_pickups(baseline_df_copy), index=baseline_df_copy.index)
    predictions_feb = pd.Series(data=get_pred_num_pickups(feb_data), index=feb_data.index)

    # Get the actual number of pickups for each zone.
    actuals_baseline = pd.Series(data=get_actual_num_pickups(baseline_df_copy), index=baseline_df_copy.index)
    actuals_feb = pd.Series(data=get_actual_num_pickups(feb_data), index=feb_data.index)

    # Add a column indicating whether each row is correct or incorrect.
    baseline_df_copy["correct"] = (predictions_baseline - actuals_baseline).abs() <= 0.2*actuals_baseline
    feb_data["correct"] = (predictions_feb - actuals_feb).abs() <= 0.2*actuals_feb

    # Add a default true column.
    baseline_df_copy["true"] = ((predictions_baseline - actuals_baseline).abs() <= 0.2*actuals_baseline) | True
    feb_data["true"] = ((predictions_feb - actuals_feb).abs() <= 0.2*actuals_feb) | True

    for metric in metrics_to_segment_by:
        baseline_data_segmented_by_metric = baseline_df_copy.groupby([metric])
        feb_data_segmented_by_metric = feb_data.groupby([metric])

        mean_baseline_trip_counts_segmented_by_metric = baseline_data_segmented_by_metric["trip_count"].mean()
        mean_feb_data_trip_counts_segmented_by_metric = feb_data_segmented_by_metric["trip_count"].mean()

        # Get number of correct counts.
        num_correct_for_baseline_data_segmented_by_metric = baseline_data_segmented_by_metric["correct"].sum()
        num_correct_for_feb_data_segmented_by_metric = feb_data_segmented_by_metric["correct"].sum()
        num_total_for_baseline_data_segmented_by_metric = baseline_data_segmented_by_metric["true"].sum()
        num_total_for_feb_data_segmented_by_metric = feb_data_segmented_by_metric["true"].sum()

        # Compute the accuracy for both sets of data
        acc_baseline_data_segmented_by_metric = 100*(num_correct_for_baseline_data_segmented_by_metric/num_total_for_baseline_data_segmented_by_metric)
        acc_feb_data_segmented_by_metric = 100*(num_correct_for_feb_data_segmented_by_metric/num_total_for_feb_data_segmented_by_metric)

        # Calculate the differences in mean and in accuracy
        diff_mean = 100*(mean_baseline_trip_counts_segmented_by_metric - mean_feb_data_trip_counts_segmented_by_metric)/mean_baseline_trip_counts_segmented_by_metric
        diff_acc = acc_baseline_data_segmented_by_metric - acc_feb_data_segmented_by_metric

        # Store the findings
        findings_mean[metric] = diff_mean
        findings_acc[metric] = diff_acc

    # Return the findings
    findings = {}
    findings["mean"] = findings_mean
    findings["acc"] = findings_acc
    return findings


def main():
    """Main drift detection analysis."""
    print("=" * 70)
    print("DRIFT DETECTION")
    print("=" * 70)

    # TODO: Load baseline and new data
    baseline, new_data = load_data()

    # TODO: Run feature-level drift detection
    feature_test_results_with_interpretations = detect_feature_drift(baseline, new_data)

    # TODO: Run concept drift detection
    concept_drift_findings = detect_concept_drift_by_segment(baseline, new_data)

    # TODO: Summarize findings
    print("Feature Drift Detection Report:")
    print("------------------------------------------")
    for metric in feature_test_results_with_interpretations:
        print(f"{metric} - p-value: {feature_test_results_with_interpretations[metric][0]}; Interpretation: {feature_test_results_with_interpretations[metric][1]}")
        print("------------------------------------------")
    print("------------------------------------------")

    print("Concept Drift Report:")
    print("------------------------------------------")
    for metric in concept_drift_findings["mean"]:
        print(f"Percentage difference for mean segmented by {metric}:")
        print(concept_drift_findings["mean"][metric])
        print("------------------------------------------")
    for metric in concept_drift_findings["acc"]:
        print(f"Difference in accuracy percentage segmented by {metric}:")
        print(concept_drift_findings["acc"][metric])
        print("------------------------------------------")


if __name__ == "__main__":
    main()
