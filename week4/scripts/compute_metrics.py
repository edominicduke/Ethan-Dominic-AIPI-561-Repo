from metric_template import *
from pathlib import Path
import lightgbm as lgb
import pandas as pd

_ROOT = Path(__file__).parent.parent.parent
MODEL_PATH = _ROOT / "week2" / "model" / "lgbm_demand_model.txt"

def load_data():
    # Load and return the baseline data and the new data.
    baseline = pd.read_parquet("week4/data/demand_enriched_baseline.parquet")
    new_data = pd.read_parquet("week4/data/demand_enriched_week4.parquet")
    return baseline, new_data

def get_pred_num_pickups(new_data):
    # Load the model.
    model = lgb.Booster(model_file=str(MODEL_PATH))

    # Make predictions for the number of trip pickups for each zone.
    pred_num_pickups = model.predict(new_data.drop(columns=["time_bucket", "trip_count"]))

    # Return the predictions for the number of trip pickups for each zone as an ndarray.
    return pred_num_pickups

def get_actual_num_pickups(new_data):
    # Get the actual number of trip pickups for each zone.
    actual_num_pickups = new_data["trip_count"]

    # Return the actual number of trip pickups for each zone as an ndarray.
    return actual_num_pickups.values

def report_metrics(results):
    # Print a report of the computed metrics.
    print("---------------------------------------------------------------------")
    print("Metrics Report:")
    for metric in results:
        if metric == "KS_Test_for_Distribution_Shift":
            print("---------------------------------------------------------------------")
            print(f"KS_Test_for_Distribution_Shift Statistic: {results[metric][0]}")
            print(f"KS_Test_for_Distribution_Shift p-value: {results[metric][1]}")
            if 0.01 < results[metric][1] <= 0.05:
                print(f"Warning: the baseline distribution for trip_count and the new distribution for trip_count is significantly different.")
            else:
                print(f"Critical: there is significant drift for trip_count. The baseline distribution for trip_count and the new distribution for trip_count is significantly different.")
        elif metric == "Duplicate_Rate":
            print("---------------------------------------------------------------------")
            print(f"Duplicate Count: {results[metric][0]}")
            print(f"Duplicate Rate: {results[metric][1]}")
            if 0 < results[metric][1] < 0.05:
                print(f"Warning: There is a noticeable percentage of duplicates in the data: {results[metric][1]}")
            elif results[metric][1] >= 0.05:
                print(f"Critical: Duplicates comprise at least 0.05% of the dataset: {results[metric][1]}")
        elif metric == "Prediction_Distribution_Shift":
            print("---------------------------------------------------------------------")
            print(f"Predictions Mean: {results[metric][0]}")
            print(f"Predictions Std: {results[metric][1]}")
            print(f"Collapsed: {results[metric][2]}")
            if results[metric][1] <= 0.35*results[metric][3]:
                print(f"Warning: The health of the model is about to collapse.")
            elif results[metric][1] <= 0.25*results[metric][3]:
                print(f"Critical: The health of the model has collapsed.")
        elif metric == "Overall_Accuracy":
            print("---------------------------------------------------------------------")
            print(f"{metric}: {results[metric]}")
            accuracy = results[metric]
            if 0.70 <= results[metric] <= 0.85:
                print(f"Warning: The overall accuracy of the model is at least 0.70: specifically {accuracy}")
            else:
                print(f"Critical: The overall accuracy of the model is below 0.70: specifically {accuracy}")
        elif metric == "Null_Rates_for_Critical_Fields":
            print("---------------------------------------------------------------------")
            print(f"{metric}: {results[metric]}")
            for null_rate_feat in results[metric]:
                if 0.5 <= results[metric][null_rate_feat] <= 1:
                    print(f"Warning: {null_rate_feat} has a null rate of {results[metric][null_rate_feat]}%")
                elif results[metric][null_rate_feat] > 1:
                    print(f"Critical: {null_rate_feat} has a null rate of {results[metric][null_rate_feat]}%")
    print("---------------------------------------------------------------------")

def main():
    # Load the baseline data and the new data.
    baseline, new_data = load_data()

    # Get the predicted number of pickups for each zone.
    predictions = get_pred_num_pickups(new_data)

    # Get the actual number of pickups for each zone.
    actuals = get_actual_num_pickups(new_data)

    # Peform metric computations.
    computer = MetricComputer(baseline)
    results = computer.compute_all_metrics(new_data, predictions, actuals)

    # Report metrics.
    report_metrics(results)

if __name__ == "__main__":
    main()