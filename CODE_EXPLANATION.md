# Detailed Explanation of `analyse_telematics_9th_nov_all_rows_july_august.py`

This document provides a step-by-step explanation of the Python script `analyse_telematics_9th_nov_all_rows_july_august.py`. The script is designed to clean, analyze, and verify telematics data from a CSV file (`vehicle_summary_aug2025.csv`).

## 1. Setup and Installation

The script begins by installing the `missingno` library, which is used for visualizing missing data.

```python
!pip install missingno --quiet
```

It then imports necessary libraries:
- `pandas` and `numpy` for data manipulation.
- `matplotlib.pyplot` for plotting.
- `missingno` for missing data visualization.
- `IPython.display` for displaying dataframes in a notebook environment.

```python
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import missingno as msno
from IPython.display import display
```

## 2. Data Loading and Initial Inspection

The script loads the dataset `vehicle_summary_aug2025.csv` into a pandas DataFrame.

```python
df = pd.read_csv('/content/vehicle_summary_aug2025.csv')
```

It then prints the shape of the dataframe (rows, columns) and displays the first few rows. It also provides a memory usage summary (`df.info()`) and descriptive statistics (`df.describe()`).

## 3. Missing Data Analysis

The script calculates the count and percentage of missing values for each column.

```python
missing = df.isna().sum().sort_values(ascending=False)
missing_pct = (missing / len(df) * 100).round(2)
```

It also visualizes the missing data pattern using a matrix plot from `missingno`. This helps identify if missingness is random or structured.

```python
msno.matrix(df, figsize=(20, 10), fontsize=12, sparkline=False)
```

## 4. Dropping Non-Informative Columns

The script identifies two types of non-informative columns:
1.  **Always Null**: Columns where all values are `NaN`.
2.  **Constant**: Columns where all rows have the same value (e.g., `START_LOCATION` might be missing for all, or `REGION_ID` might be the same for all).

```python
always_null = df.columns[df.isna().all()].tolist()
constant_cols = df.columns[df.nunique(dropna=False) <= 1].tolist()
```

These columns are then dropped from the dataframe to reduce noise.

Additionally, a specific list of columns (identified from prior analysis) is defined and dropped. This list includes columns like `START_LOCATION`, `TOTAL_ALERT_COUNT`, `AVG_NO_OF_PASSENGERS`, etc.

```python
cols_to_drop = list(set(always_null_cols + constant_cols))
df_clean = df.drop(columns=cols_to_drop)
```

## 5. Duplicate and Integrity Checks

### Duplicates
The script checks for:
- Full row duplicates.
- Duplicates based on `VEHICLE_ID` (expecting one record per vehicle).
- Duplicates based on `VIN_NO`.

```python
full_dupes = df_clean[df_clean.duplicated()]
dup_vehicle_id = df_clean['VEHICLE_ID'].duplicated().sum()
```

### Data Integrity
The script performs several sanity checks:
- **Negative Values**: Checks for negative values in numeric columns (which shouldn't exist for counts or distances).
- **Speed Limits**: Checks if `MAX_SPEED` exceeds 200 km/h (outliers).
- **Odometer Logic**: Checks if `END_ODOMETER` is less than `START_ODOMETER`.
- **Engine Hours**: Checks if `TOTAL_ENGINE_HOURS` exceeds 24 hours (impossible for a daily summary, though the file seems to be a monthly summary based on the name, the logic checks for >24 which implies a daily check, or perhaps the unit is misunderstood). *Correction based on later code*: The script later notes that `STOP_ENGINE_HOURS` has frequent values like 744 (31 days * 24 hours), implying it's a monthly summary.

```python
invalid_odo = df_clean[df_clean['END_ODOMETER'] < df_clean['START_ODOMETER']]
```

## 6. Specific Data Cleaning

Based on the integrity checks, the script filters the data:
- Removes rows with negative `HOUR_METER`.
- Removes rows where `STOP_ENGINE_HOURS` > 744 (more than total hours in August).
- Drops rows with missing odometer readings (optional step in code).
- Drops engine-hour related columns (`MOVE_ENGINE_HOURS`, `STOP_ENGINE_HOURS`, etc.) as they were deemed non-informative or redundant.

```python
df_clean = df_clean[df_clean['HOUR_METER'] >= 0]
df_clean = df_clean[df_clean['STOP_ENGINE_HOURS'] <= 744]
```

## 7. Column Selection and Quality Scoring

The script selects a specific subset of ~86 columns considered relevant for telematics analysis (e.g., `DISTANCE_TRAVELED`, `FUEL_CONSUMED`, `MAX_SPEED`, `Idling` metrics, etc.).

It then calculates a "Data Quality Score" for each column based on:
- **Missing %**: Percentage of `NaN` values.
- **Zero %**: Percentage of values equal to 0.
- **Constant %**: Percentage of constant values.

A `Total_%` score is created by summing these. Columns with `Total_% > 50` are considered "low quality" and dropped.

```python
data_quality_summary['Total_%'] = data_quality_summary[['Missing_%', 'Zero_%', 'Constant_%']].sum(axis=1)
informative_cols = data_quality_summary[data_quality_summary['Total_%'] <= 50].index.tolist()
df_final = df_sub[informative_cols].copy()
```

## 8. Exporting Cleaned Data

The script exports the first 15 rows of the final cleaned dataframe to a CSV file.

```python
df_final.head(15).to_csv('15_left_35.csv')
```

## 9. Verification of Derived Metrics

The final section of the script attempts to verify the calculated fields present in the data by re-deriving them from raw fields.

### Key Formulas Used:
- **active_days**: `total_days_in_month - NO_RUN_DAYS`
- **computed_distance**: `END_ODOMETER - START_ODOMETER`
- **exp_AVG_TRIPS_PER_DAY**: `NO_OF_TRIPS / active_days`
- **exp_AVG_DISTANCE**: `DISTANCE_TRAVELED / active_days`
- **exp_AVG_RUN_TIME**: `MOVE_MINS / active_days`
- **exp_AVG_IDLE_TIME**: `IDLE_MINS / total_days` (Note: uses total days, not active days)

### Comparison (Delta Analysis):
The script calculates the difference (`delta`) between the value provided in the dataset and the value calculated using the formulas above.

```python
df['delta_AVG_TRIPS_PER_DAY'] = df['AVG_TRIPS_PER_DAY'] - df['exp_AVG_TRIPS_PER_DAY']
```

### Findings/Inferences from the Script:
- **AVG_TRIPS_PER_DAY, AVG_RUN_TIME, AVG_IDLE_TIME**: matches the re-calculated values consistently.
- **DISTANCE_TRAVELED**: Does *not* match `END_ODOMETER - START_ODOMETER`. This implies `DISTANCE_TRAVELED` comes from a different source (e.g., GPS distance) rather than raw odometer readings.
- **AVG_DISTANCE**: Does *not* match `DISTANCE_TRAVELED / active_days`. This suggests the source system uses a different logic for "active days" when calculating average distance (perhaps excluding days with very short trips).

## 10. Summary

The script acts as a comprehensive data quality and validation pipeline. It starts with raw data, removes noise (empty/constant columns), filters invalid records (negative timers), selects high-quality features, and finally audits the mathematical consistency of the reported metrics against standard formulas.
