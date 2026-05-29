"""
Data Quality Validation Framework Template

This file is a starting point for your validation code.
Modify or replace as needed based on the issues you identify.
"""

import pandas as pd
import numpy as np
from typing import Dict, List


class DataQualityValidator:
    """Validates data against quality expectations."""

    def __init__(self, baseline_df: pd.DataFrame = None):
        """
        Initialize validator.

        Args:
            baseline_df: Clean reference data for comparison
        """
        self.baseline = baseline_df
        self.issues = []

    def validate(self, df: pd.DataFrame) -> Dict:
        """
        Run all validation checks.

        Returns:
            Dictionary with:
            - is_valid: boolean
            - num_issues: count of issues found
            - issues: list of issue details
        """
        self.issues = []

        # TODO: Add your validation checks here
        # Example structure:
        self.check_null_rates(df)
        self.check_value_ranges(df)
        self.check_duplicates(df)
        self.check_distributions(df)
        self.check_schema(df)

        return {
            "is_valid": len(self.issues) == 0,
            "num_issues": len(self.issues),
            "issues": self.issues,
        }

    def check_null_rates(self, df: pd.DataFrame):
        """Check if any column has excessive nulls."""
        # TODO: Implement
        # What threshold is acceptable? (depends on your data)
        # Which columns are critical (can't have any nulls)?
        """
        Recall the following API specifications:
        /api/heatmap — zone-level demand heatmap (parameters: hour, dow, date, holiday)
        /api/forecast — multi-step demand forecast for a specific zone (parameters: zone_id, hour, dow, steps, date)
        /api/recommendations — ranked zone recommendations for driver positioning (parameters: zone_id, hour, dow, n, date)

        Further consider the following function implementations located in data.py:
        - def get_heatmap(hour: int, dow: int, holiday: str = "regular", date: str = None)
        - def forecast_demand(zone_id: int, hour: int, dow: int, num_steps: int = 16, date: str = None)
        - def get_recommendations(zone_id: int, hour: int, dow: int, n: int = 3, holiday: str = "regular", date: str = None)

        In these implementations, hour, dow, and zone_id do not have default values. Therefore, these columns in specific cannot have any nulls.
        """

        # Define the columns that cannot have any nulls
        columns_with_zero_nulls = ["hour", "dayofweek", "PULocationID"]
        
        # Initialize issue flags
        add_critical_null_issue = False
        add_low_null_issue = False
        add_medium_null_issue = False
        add_high_null_issue = False

        # Initialize lists to store columns with nulls as appropriate
        critical_columns_with_nulls = []
        low_columns_with_nulls = []
        medium_columns_with_nulls = []
        high_columns_with_nulls = []
        
        # Update said lists with the appropriate columns
        for column in df:
            if column in columns_with_zero_nulls:
                if df[column].isna().mean() > 0:
                    add_critical_null_issue = True
                    critical_columns_with_nulls.append(column)
            elif df[column].isna().mean() > 0.01:
                if df[column].isna().mean() < 0.05*df[column].size:
                    add_low_null_issue = True
                    low_columns_with_nulls.append(column)
                elif df[column].isna().mean() < 0.20*df[column].size:
                    add_medium_null_issue = True
                    medium_columns_with_nulls.append(column)
                else:
                    add_high_null_issue = True
                    high_columns_with_nulls.append(column)

        # Add issues as appropriate
        if add_critical_null_issue:
            for column in critical_columns_with_nulls:
                self._add_issue(
                    issue_type="Critical column has nulls",
                    severity='Critical',
                    description=f"{column} has a null rate of {df[column].isna().mean()}",
                    count=None
                )
        if add_low_null_issue:
            for column in low_columns_with_nulls:
                self._add_issue(
                    issue_type="Noncritical column has a null rate less than 5%",
                    severity='Low',
                    description=f"{column} has a null rate of {df[column].isna().mean()}",
                    count=None
                )
        if add_medium_null_issue:
            for column in medium_columns_with_nulls:
                self._add_issue(
                    issue_type="Noncritical column has a null rate less than 20%",
                    severity='Medium',
                    description=f"{column} has a null rate of {df[column].isna().mean()}",
                    count=None
                )
        if add_high_null_issue:
            for column in high_columns_with_nulls:
                self._add_issue(
                    issue_type="Noncritical column has a null rate greater than 20%",
                    severity='High',
                    description=f"{column} has a null rate of {df[column].isna().mean()}",
                    count=None
                )

    def check_value_ranges(self, df: pd.DataFrame):
        """Check if values fall within expected ranges."""
        # TODO: Implement
        # Examples:
        # - trip_count should be >= 0
        # - hour should be 0-23
        # - dayofweek should be 0-6
        # - zone IDs should be valid

        trip_count_col = df["trip_count"]
        if trip_count_col[trip_count_col < 0].size > 0:
            self._add_issue(
                issue_type="Negative trip counts are being predicted",
                severity='Critical',
                description=f"There are {trip_count_col[trip_count_col < 0].size} instances of these negative counts.",
                count=trip_count_col[trip_count_col < 0].size
            )

        hour_col = df["hour"]
        if hour_col[hour_col < 0].size > 0 or hour_col[hour_col > 23].size > 0:
            self._add_issue(
                issue_type="Hour values are out of range",
                severity='Critical',
                description=f"There are {hour_col[hour_col < 0].size + hour_col[hour_col > 23].size} instances of these out of range values.",
                count=(hour_col[hour_col < 0].size + hour_col[hour_col > 23].size)
            )

        dayofweek_col = df["dayofweek"]
        if dayofweek_col[dayofweek_col < 0].size > 0 or dayofweek_col[dayofweek_col > 6].size > 0:
            self._add_issue(
                issue_type="dayofweek values are out of range",
                severity='Critical',
                description=f"There are {dayofweek_col[dayofweek_col < 0].size + dayofweek_col[dayofweek_col > 6].size} instances of these out of range values.",
                count=(dayofweek_col[dayofweek_col < 0].size + dayofweek_col[dayofweek_col > 6].size)
            )

        zone_id_col = df["PULocationID"]
        if zone_id_col[zone_id_col < 0].size > 0 or zone_id_col[zone_id_col > 265].size > 0:
            self._add_issue(
                issue_type="PULocationID values are out of range",
                severity='Critical',
                description=f"There are {zone_id_col[zone_id_col < 0].size + zone_id_col[zone_id_col > 265].size} instances of these out of range values.",
                count=(zone_id_col[zone_id_col < 0].size + zone_id_col[zone_id_col > 265].size)
            )

    def check_distributions(self, df: pd.DataFrame):
        """Check if data distribution matches baseline."""
        # TODO: Implement
        # Examples:
        # - Outlier detection (values >N sigma from mean)
        # - Median/mean comparison to baseline
        # - Quantile comparisons

        # Compute the percentage differences between the feature means of the corrupted data and the baseline data.
        corrupted_means = df.drop(columns=["time_bucket"]).mean()
        baseline_means = self.baseline.drop(columns=["time_bucket"]).mean()
        mean_percentage_diff = 100*((corrupted_means - baseline_means)/baseline_means).abs()

        # Compute the percentage differences between the feature stds of the corrupted data and the baseline data.
        corrupted_stds = df.drop(columns=["time_bucket"]).std()
        baseline_stds = self.baseline.drop(columns=["time_bucket"]).std()
        std_percentage_diff = 100*((corrupted_stds - baseline_stds)/baseline_stds).abs()

        # Add issues as appropriate depending on the percentage difference magnitudes.

        if mean_percentage_diff.values.max() > 0:
            if mean_percentage_diff.values.max() < 5:
                self._add_issue(
                    issue_type="There are percentage differences between the feature means of the corrupted data and the baseline data",
                    severity='Low',
                    description=f"These percentage differences are less than 5%",
                    count=None
                )
            elif mean_percentage_diff.values.max() < 10:
                self._add_issue(
                    issue_type="There are percentage differences between the feature means of the corrupted data and the baseline data",
                    severity='Medium',
                    description=f"These percentage differences are less than 10%",
                    count=None
                )
            elif mean_percentage_diff.values.max() < 20:
                self._add_issue(
                    issue_type="There are percentage differences between the feature means of the corrupted data and the baseline data",
                    severity='High',
                    description=f"These percentage differences are less than 20%",
                    count=None
                )
            else:
                self._add_issue(
                    issue_type="There are percentage differences between the feature means of the corrupted data and the baseline data",
                    severity='Critical',
                    description=f"Some percentage differences are greater than 20%",
                    count=None
                )
        
        if std_percentage_diff.values.max() > 0:
            if std_percentage_diff.values.max() < 5:
                self._add_issue(
                    issue_type="There are percentage differences between the feature standard deviations of the corrupted data and the baseline data",
                    severity='Low',
                    description=f"These percentage differences are less than 5%",
                    count=None
                )
            elif std_percentage_diff.values.max() < 10:
                self._add_issue(
                    issue_type="There are percentage differences between the feature standard deviations of the corrupted data and the baseline data",
                    severity='Medium',
                    description=f"These percentage differences are less than 10%",
                    count=None
                )
            elif std_percentage_diff.values.max() < 20:
                self._add_issue(
                    issue_type="There are percentage differences between the feature standard deviations of the corrupted data and the baseline data",
                    severity='High',
                    description=f"These percentage differences are less than 20%",
                    count=None
                )
            else:
                self._add_issue(
                    issue_type="There are percentage differences between the feature standard deviations of the corrupted data and the baseline data",
                    severity='Critical',
                    description=f"Some percentage differences are greater than 20%",
                    count=None
                )


    def check_duplicates(self, df: pd.DataFrame):
        """Check for duplicate rows."""
        # TODO: Implement
        # What counts as a duplicate? All columns or key columns only? - Will count all columns

        # Calculate the number of duplicates in the data.
        num_duplicates = df.duplicated().sum()

        # Add issues as appropriate depending on the proportion of the dataset the duplicates make up.
        if num_duplicates > 0:
            if num_duplicates < 0.01*df.shape[0]:
                self._add_issue(
                    issue_type="There are duplicates present in the dataset",
                    severity='Low',
                    description=f"The duplicates make up less than 1% of the datset",
                    count=None
                )
            elif num_duplicates < 0.05*df.shape[0]:
                self._add_issue(
                    issue_type="There are duplicates present in the dataset",
                    severity='Medium',
                    description=f"The duplicates make up less than 5% of the datset",
                    count=None
                )
            elif num_duplicates < 0.1*df.shape[0]:
                self._add_issue(
                    issue_type="There are duplicates present in the dataset",
                    severity='High',
                    description=f"The duplicates make up less than 10% of the datset",
                    count=None
                )
            else:
                self._add_issue(
                    issue_type="There are duplicates present in the dataset",
                    severity='Critical',
                    description=f"The duplicates make up more than 10% of the datset",
                    count=None
                )

    def check_schema(self, df: pd.DataFrame):
        """Check that required columns exist with correct types."""
        # TODO: Implement
        # What columns are required? Any columns that exist in the baseline data (especially hour, dow, and zone_id which cannot afford to have any null values).
        # What types should they be? The same types as those in the baseline data.

        # Keep a count of the number of missing columns as well as the number of incorrectly typed columns.
        num_missing_cols = 0
        num_incorrect_type_cols = 0

        # Update these counts.
        for baseline_column in self.baseline.columns.tolist():
            if not(baseline_column in df.columns.tolist()):
                num_missing_cols += 1
        for df_column in df.columns.tolist():
            for baseline_column in self.baseline.columns.tolist():
                if df_column == baseline_column:
                    if not(df[df_column].dtype == self.baseline[baseline_column].dtype):
                        num_incorrect_type_cols += 1

        # Add issues based on these counts.
        if num_missing_cols > 0:
            self._add_issue(
                issue_type="The corrupted data is missing columns",
                severity='Critical',
                description=f"There are {num_missing_cols} missing columns",
                count=num_missing_cols
            )
        if num_incorrect_type_cols > 0:
            self._add_issue(
                issue_type="Some of the corrupted data's columns are incorrect in terms of type",
                severity='Critical',
                description=f"There are {num_incorrect_type_cols} incorrectly typed columns",
                count=num_incorrect_type_cols
            )

    def _add_issue(
        self,
        issue_type: str,
        severity: str,
        description: str,
        count: int = None,
        **details
    ):
        """Helper to add issue to list."""
        issue = {
            "type": issue_type,
            "severity": severity,  # 'critical', 'high', 'medium', 'low'
            "description": description,
            "count": count,
            **details,
        }
        self.issues.append(issue)