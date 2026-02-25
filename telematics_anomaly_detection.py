"""
Script to detect anomalies in telematics data.

Usage:
1. Ensure pandas is installed: pip install pandas
2. Set the FILEPATH variable in the main block to your CSV file path.
3. Run the script: python telematics_anomaly_detection.py
"""

import pandas as pd
import numpy as np
import os

def load_data(filepath):
    """Loads the dataset from a CSV file."""
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return None
    try:
        df = pd.read_csv(filepath)
        print(f"Dataset loaded successfully. Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

def check_odometer_mismatch(df):
    """Checks for odometer mismatch where (End - Start) != Distance Traveled."""
    print("\n--- DATA CONSISTENCY ANOMALY: ODOMETER MISMATCH ---")
    required_cols = ['START_ODOMETER', 'END_ODOMETER', 'DISTANCE_TRAVELED']
    if not all(col in df.columns for col in required_cols):
        print(f"Skipping check: Missing columns {set(required_cols) - set(df.columns)}")
        return

    # Calculate difference
    df['odo_diff'] = df['END_ODOMETER'] - df['START_ODOMETER']
    df['mismatch'] = (df['odo_diff'] - df['DISTANCE_TRAVELED']).abs()

    # Threshold for mismatch (e.g., > 0.1 km)
    mismatched_df = df[df['mismatch'] > 0.1]

    print(f"Vehicles with odometer mismatch: {len(mismatched_df)}")

    if 'org_id' in df.columns and not mismatched_df.empty:
        print(f"Top 5 Organizations with mismatches:\n{mismatched_df['org_id'].value_counts().head()}")

    if not mismatched_df.empty and 'VEHICLE_ID' in df.columns:
        max_mismatch_idx = mismatched_df['mismatch'].idxmax()
        max_row = mismatched_df.loc[max_mismatch_idx]
        print(f"Vehicle with max mismatch: ID {max_row['VEHICLE_ID']}, Mismatch: {max_row['mismatch']:.2f}")

def check_harsh_acceleration(df):
    """Checks for high harsh acceleration alert counts."""
    print("\n--- HARSH_ACC_ALERT_COUNT ANALYSIS ---")
    if 'HARSH_ACC_ALERT_COUNT' not in df.columns:
        print("Column 'HARSH_ACC_ALERT_COUNT' missing.")
        return

    high_acc = df[df['HARSH_ACC_ALERT_COUNT'] > 50]
    print(f"Vehicles with > 50 harsh acceleration alerts: {len(high_acc)}")

    if not high_acc.empty:
        max_acc_idx = df['HARSH_ACC_ALERT_COUNT'].idxmax()
        print(f"Max Harsh Accel Count: {df.loc[max_acc_idx, 'HARSH_ACC_ALERT_COUNT']} (Vehicle ID: {df.loc[max_acc_idx, 'VEHICLE_ID']})")
        if 'org_id' in df.columns:
             print(f"Top Org: {high_acc['org_id'].value_counts().idxmax()}")

def check_harsh_braking(df):
    """Checks for high harsh braking alert counts."""
    print("\n--- HARSH_BRAKE_ALERT_COUNT ANALYSIS ---")
    if 'HARSH_BRAKE_ALERT_COUNT' not in df.columns:
        print("Column 'HARSH_BRAKE_ALERT_COUNT' missing.")
        return

    high_brake = df[df['HARSH_BRAKE_ALERT_COUNT'] > 50]
    print(f"Vehicles with > 50 harsh brake alerts: {len(high_brake)}")

    if not high_brake.empty:
        max_brake_idx = df['HARSH_BRAKE_ALERT_COUNT'].idxmax()
        print(f"Max Harsh Brake Count: {df.loc[max_brake_idx, 'HARSH_BRAKE_ALERT_COUNT']} (Vehicle ID: {df.loc[max_brake_idx, 'VEHICLE_ID']})")
        if 'org_id' in df.columns:
             print(f"Top Org: {high_brake['org_id'].value_counts().idxmax()}")

def check_hourmeter_mismatch(df):
    """Checks for hourmeter mismatch."""
    print("\n--- HOURMETER MISMATCH & TOTAL HOURMETER ERROR ---")

    required_cols = ['START_HOURMETER', 'END_HOURMETER']
    if not all(col in df.columns for col in required_cols):
        print(f"Skipping check: Missing columns {set(required_cols) - set(df.columns)}")
        return

    # Check missing
    print(f"Missing START_HOURMETER: {df['START_HOURMETER'].isna().sum()}")
    print(f"Missing END_HOURMETER: {df['END_HOURMETER'].isna().sum()}")

    valid_hm = df.dropna(subset=required_cols).copy()
    valid_hm['hm_diff'] = valid_hm['END_HOURMETER'] - valid_hm['START_HOURMETER']

    # Check 1: Mismatch with HOUR_METER
    if 'HOUR_METER' in df.columns:
        print("\nChecking HOUR_METER Mismatch...")
        mismatch_hm = valid_hm[valid_hm['HOUR_METER'].notna()]
        mismatch_hm = mismatch_hm[(mismatch_hm['hm_diff'] - mismatch_hm['HOUR_METER']).abs() > 0.1]
        print(f"Vehicles with HOUR_METER mismatch: {len(mismatch_hm)}")
        if not mismatch_hm.empty and 'org_id' in df.columns:
            print(f"Top Organizations (HOUR_METER):\n{mismatch_hm['org_id'].value_counts().head()}")

    # Check 2: Calculation Error with TOTAL_HOURMETER
    if 'TOTAL_HOURMETER' in df.columns:
        print("\nChecking TOTAL_HOURMETER Calculation Error...")
        mismatch_tot = valid_hm[valid_hm['TOTAL_HOURMETER'].notna()]
        mismatch_tot = mismatch_tot[(mismatch_tot['hm_diff'] - mismatch_tot['TOTAL_HOURMETER']).abs() > 0.1]
        print(f"Records with TOTAL_HOURMETER Calculation Error: {len(mismatch_tot)}")

def check_abnormal_idle(df):
    """Checks for abnormal idle minutes."""
    print("\n--- ABNORMAL IDLE_MINS ---")
    if 'IDLE_MINS' not in df.columns:
        print("Column 'IDLE_MINS' missing.")
        return

    abnormal_idle = df[df['IDLE_MINS'] > 13000]
    print(f"Vehicles with > 13000 idle mins: {len(abnormal_idle)}")

    if not abnormal_idle.empty:
        max_idle_idx = df['IDLE_MINS'].idxmax()
        print(f"Max Idle Mins: {df.loc[max_idle_idx, 'IDLE_MINS']} (Vehicle ID: {df.loc[max_idle_idx, 'VEHICLE_ID']})")
        if 'org_id' in df.columns:
             print(f"Top Org: {abnormal_idle['org_id'].value_counts().idxmax()}")

def check_alert_counts(df):
    """Checks SPEED, MPR, and OVER_SPEED alert counts."""
    print("\n--- ALERT COUNT ANALYSES ---")

    for col in ['SPEED_ALERT_COUNT', 'MPR_ALERT_COUNT', 'OVER_SPEED_COUNT']:
        if col in df.columns:
            high = df[df[col] > 50]
            print(f"Vehicles with > 50 {col}: {len(high)}")
            if not high.empty:
                max_row = df.loc[df[col].idxmax()]
                print(f"Max {col}: {max_row[col]} (Vehicle ID: {max_row['VEHICLE_ID']})")
                if 'org_id' in df.columns:
                    print(f"Top Org ({col}): {high['org_id'].value_counts().idxmax()}")

def check_over_time_columns(df):
    """Checks for missing data in OVER_TIME_* columns."""
    print("\n--- OVER_TIME COLUMNS ANALYSIS ---")
    cols = ['OVER_TIME_DISTANCE_TRAVELLED', 'OVER_TIME_MOVE_MINS', 'OVER_TIME_IDLE_MINS', 'OVER_TIME_STOP_MINS']
    for col in cols:
        if col in df.columns:
            # Check non-null and non-zero (assuming 0 might indicate missing/default)
            count = df[col].replace(0, np.nan).count()
            print(f"{col}: {count} non-zero records.")
        else:
            print(f"{col} missing from dataset.")

def check_geo_alerts(df):
    """Checks GEO_ALERT_COUNT."""
    print("\n--- GEO_ALERT_COUNT ANALYSIS ---")
    if 'GEO_ALERT_COUNT' not in df.columns: return

    missing = df['GEO_ALERT_COUNT'].isna().sum()
    print(f"Missing GEO_ALERT_COUNT: {missing}")

    high_geo = df[df['GEO_ALERT_COUNT'] > 50]
    print(f"Vehicles with > 50 GEO_ALERT_COUNT: {len(high_geo)}")
    if not high_geo.empty:
        print(f"Max Geo Alert: {df.loc[df['GEO_ALERT_COUNT'].idxmax(), 'GEO_ALERT_COUNT']}")

def check_abnormal_distance(df):
    """Checks for abnormal distance traveled (> 40,000 km)."""
    print("\n--- ABNORMAL DISTANCE TRAVELED (> 40,000 km) ---")
    if 'DISTANCE_TRAVELED' in df.columns:
        high_dist = df[df['DISTANCE_TRAVELED'] > 40000]
        print(f"Vehicles with > 40,000 km distance: {len(high_dist)}")
        for _, row in high_dist.iterrows():
            print(f"Vehicle ID: {row['VEHICLE_ID']}, Distance: {row['DISTANCE_TRAVELED']}")

def check_null_constant_columns(df):
    """Identifies always null or constant columns."""
    print("\n--- NULL AND CONSTANT COLUMNS ---")
    always_null = df.columns[df.isna().all()].tolist()
    constant = df.columns[df.nunique(dropna=False) <= 1].tolist()

    print(f"Always Null Columns ({len(always_null)}): {always_null[:5]} ...")
    print(f"Constant Columns ({len(constant)}): {constant[:5]} ...")

def check_odometer_jumps(df):
    """Checks for odometer jumps between consecutive records for the same vehicle."""
    print("\n--- ODOMETER JUMP ANOMALIES ---")
    req_cols = ['VEHICLE_ID', 'START_ODOMETER', 'END_ODOMETER']
    time_col = next((c for c in df.columns if 'DATE' in c or 'TIME' in c), None) # Guess time column

    if not all(col in df.columns for col in req_cols) or not time_col:
        print("Skipping Odometer Jump check: Missing columns or time column.")
        return

    # Sort
    df_sorted = df.sort_values(by=['VEHICLE_ID', time_col])

    # Check conditions: Same vehicle, Start Odo != Prev End Odo
    df_sorted['prev_vehicle'] = df_sorted['VEHICLE_ID'].shift(1)
    df_sorted['prev_end_odo'] = df_sorted['END_ODOMETER'].shift(1)

    jumps = df_sorted[
        (df_sorted['VEHICLE_ID'] == df_sorted['prev_vehicle']) &
        (df_sorted['START_ODOMETER'] != df_sorted['prev_end_odo'])
    ]

    print(f"Odometer Jump Anomalies found: {len(jumps)} ({len(jumps)/len(df)*100:.2f}%)")

def check_special_anomalies(df):
    """Checks for specific anomalies mentioned in the prompt."""
    print("\n--- SPECIAL ANOMALIES ---")

    # 1. EXCESSIVE RPM
    if 'MAX_RPM' in df.columns:
        high_rpm = df[df['MAX_RPM'] > 7000]
        print(f"Vehicles with RPM > 7000: {len(high_rpm)}")

    # 2. NEGATIVE DRIVER SCORE
    ds_col = next((c for c in df.columns if 'DRIVER' in c and 'SCORE' in c), None)
    if ds_col:
        neg_score = df[df[ds_col] < 0]
        print(f"Negative Driver Score records: {len(neg_score)}")

    # 3. UNREALISTIC VEHICLE SPEED
    if 'MAX_SPEED' in df.columns:
        high_speed = df[df['MAX_SPEED'] >= 200]
        print(f"Vehicles with Speed >= 200 km/h: {len(high_speed)}")

    # 4. MAX_RPM_COOL_TEMP Anomaly (Temp=0, Dist>0)
    if 'MAX_RPM_COOL_TEMP' in df.columns and 'DISTANCE_TRAVELED' in df.columns:
        anom = df[(df['MAX_RPM_COOL_TEMP'] == 0) & (df['DISTANCE_TRAVELED'] > 0)]
        print(f"MAX_RPM_COOL_TEMP=0 & Dist>0 Anomaly: {len(anom)}")

    # 5. MAF/IMAP Anomaly (Guessing column names)
    maf_col = next((c for c in df.columns if 'MAF' in c), None)
    imap_col = next((c for c in df.columns if 'IMAP' in c), None)
    if maf_col and imap_col and 'DISTANCE_TRAVELED' in df.columns:
        zeros = df[(df[maf_col] == 0) & (df[imap_col] == 0) & (df['DISTANCE_TRAVELED'] > 0)]
        print(f"MAF/IMAP=0 & Dist>0 Anomaly: {len(zeros)}")

    # 6. NIGHT DRIVING
    if 'NIGHT_DRIVING_DISTANCE' in df.columns and 'NIGHT_MOVING_MINS' in df.columns:
        anom1 = df[(df['NIGHT_DRIVING_DISTANCE'] > 0) & (df['NIGHT_MOVING_MINS'] == 0)]
        print(f"Night Dist > 0 but Mins = 0: {len(anom1)}")

        anom2 = df[(df['NIGHT_DRIVING_DISTANCE'] == 0) & (df['NIGHT_MOVING_MINS'] > 0)]
        print(f"Night Dist = 0 but Mins > 0: {len(anom2)}")

    # 7. MAX SPEED vs RPM AT MAX SPEED
    if 'MAX_SPEED' in df.columns and 'RPM_AT_MAX_SPEED' in df.columns:
        anom = df[(df['RPM_AT_MAX_SPEED'] == 0) & (df['MAX_SPEED'] > 0)]
        print(f"RPM_AT_MAX_SPEED=0 & MAX_SPEED>0 Anomaly: {len(anom)}")

    # 8. EXCESSIVE DAILY DISTANCE (> 2000 km)
    if 'DISTANCE_TRAVELED' in df.columns:
        high_daily = df[df['DISTANCE_TRAVELED'] > 2000]
        print(f"Distance > 2000 km (Excessive for 1 day): {len(high_daily)}")

    # 9. MOVE MINS VS DISTANCE
    if 'MOVE_MINS' in df.columns and 'DISTANCE_TRAVELED' in df.columns:
        anom = df[(df['MOVE_MINS'] > 0) & (df['DISTANCE_TRAVELED'] == 0)]
        print(f"Move Mins > 0 but Distance = 0: {len(anom)}")

    # 10. DISTANCE > 0 FUEL = 0
    if 'DISTANCE_TRAVELED' in df.columns and 'FUEL_CONSUMED' in df.columns:
        anom = df[(df['DISTANCE_TRAVELED'] > 0) & (df['FUEL_CONSUMED'] == 0)]
        print(f"Distance > 0 but Fuel = 0: {len(anom)}")

if __name__ == "__main__":
    FILEPATH = 'vehicle_summary_aug2025.csv'

    print(f"Analyzing file: {FILEPATH}")
    df = load_data(FILEPATH)

    if df is not None:
        check_odometer_mismatch(df)
        check_harsh_acceleration(df)
        check_harsh_braking(df)
        check_hourmeter_mismatch(df)
        check_abnormal_idle(df)
        check_alert_counts(df)
        check_over_time_columns(df)
        check_geo_alerts(df)
        check_abnormal_distance(df)
        check_null_constant_columns(df)
        check_odometer_jumps(df)
        check_special_anomalies(df)
