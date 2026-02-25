# Telematics Anomaly Detection Script Explanation

This document explains the Python script `telematics_anomaly_detection.py`, which is designed to identify specific data anomalies and observations in a telematics dataset.

## Purpose

The script loads a CSV file containing vehicle telematics data and performs a series of checks to detect:
- Data consistency issues (e.g., Odometer vs Distance Traveled).
- Abnormal driver behavior (e.g., Harsh Acceleration, Braking, Speeding).
- Sensor malfunctions (e.g., Hourmeter mismatch, Coolant Temp anomalies).
- Missing data patterns (e.g., Over-time columns, Geo alerts).
- Logical inconsistencies (e.g., Moving while RPM is 0, Fuel consumed is 0 while moving).

## Key Functions

### 1. `load_data(filepath)`
Loads the dataset using pandas. Handles file not found errors.

### 2. `check_odometer_mismatch(df)`
Calculates the difference between `END_ODOMETER` and `START_ODOMETER` and compares it with `DISTANCE_TRAVELED`.
- **Logic:** `abs((END - START) - DISTANCE) > Threshold (0.1)`
- **Output:** Count of mismatched vehicles and top organizations.

### 3. Alert Count Checks
- `check_harsh_acceleration(df)`: Checks for `HARSH_ACC_ALERT_COUNT > 50`.
- `check_harsh_braking(df)`: Checks for `HARSH_BRAKE_ALERT_COUNT > 50`.
- `check_alert_counts(df)`: Checks for Speed, MPR, and Over Speed alerts > 50.

### 4. `check_hourmeter_mismatch(df)`
Verifies hourmeter consistency in two ways:
1. `(END_HOURMETER - START_HOURMETER)` vs `HOUR_METER` column.
2. `(END_HOURMETER - START_HOURMETER)` vs `TOTAL_HOURMETER` column (if present).

### 5. `check_abnormal_idle(df)`
Identifies vehicles with `IDLE_MINS > 13000`.

### 6. `check_special_anomalies(df)`
A comprehensive function checking for various logical anomalies:
- **Excessive RPM**: `MAX_RPM > 7000`.
- **Negative Driver Score**: Checks for values < 0 in driver score columns.
- **Unrealistic Speed**: `MAX_SPEED >= 200` km/h.
- **Sensor Conflicts**:
    - `MAX_RPM_COOL_TEMP == 0` while `DISTANCE_TRAVELED > 0`.
    - `MAF` & `IMAP` sensors == 0 while `DISTANCE_TRAVELED > 0`.
    - `RPM_AT_MAX_SPEED == 0` while `MAX_SPEED > 0`.
- **Night Driving Inconsistency**:
    - Distance > 0 but Minutes = 0.
    - Distance = 0 but Minutes > 0.
- **Move Mins vs Distance**: Moving time recorded but 0 distance.
- **Fuel vs Distance**: Distance recorded but 0 fuel consumed.

### 7. `check_odometer_jumps(df)`
Checks if the `START_ODOMETER` of a trip matches the `END_ODOMETER` of the previous trip for the same vehicle. Requires sorting by time.

## Usage

1.  Ensure **pandas** is installed: `pip install pandas`
2.  Open `telematics_anomaly_detection.py` and set the `FILEPATH` variable to your CSV file location (default: `vehicle_summary_aug2025.csv`).
3.  Run the script:
    ```bash
    python telematics_anomaly_detection.py
    ```
