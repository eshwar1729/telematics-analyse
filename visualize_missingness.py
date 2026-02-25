import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# --- Data ---
data = {
    "column": [
        "MAX_RPM_OIL_PRESSURE", "END_FLS_LEVEL", "TRIP_REFILL_EVENT", "TRIP_FUEL_REFILL_VALUE",
        "FUEL_CONSUMED", "AD_BLUE_CONSUMED", "CAN_END_ODOMETER", "CAN_START_ODOMETER",
        "CAN_DISTANCE_TRAVELLED", "CAN_REVERSE_MOVE", "CAN_FORWARD_MOVE", "IDLE_ALERT_COUNT",
        "SPEED_ALERT_COUNT", "REVERSE_MOVE_MINS", "TOTAL_CAN_HOURMETER", "END_GPS_HOURMETER",
        "START_GPS_HOURMETER", "IMPACT_ALERT_COUNT", "RASH_TURNING_COUNT", "END_HOURMETER",
        "START_HOURMETER", "GEO_ALERT_COUNT", "WORKING_OFFLINE_MINS", "WORKING_STOP_MINS",
        "WORKING_MOVE_MINS", "FORWARD_MOVE_MINS", "MPR_ALERT_COUNT", "TOTAL_HOUR_METER",
        "AVG_BATTERY_VOLTAGE", "BATTERY_CUMULATIVE_VOLTAGE", "IMAP", "MAF",
        "HARSH_BRAKE_ALERT_COUNT", "HARSH_ACC_ALERT_COUNT", "OVER_SPEED_DURATION",
        "OVER_SPEED_COUNT", "OFFLINE_MINS", "COOLANT_TEMP_ALERT_COUNT", "RPM_AT_MAX_SPEED",
        "MAX_RPM_COOL_TEMP", "SPEED_AT_MAX_RPM", "MAX_RPM", "ENGINE_RUN_MINS", "NIGHT_IDLE_MINS",
        "DRIVER_SCORE", "NIGHT_DRIVING_DISTANCE", "NIGHT_MOVING_MINS", "IDLE_COUNT_MINS",
        "IDLE_COUNT", "IDLE_PERCENT", "IDLE_MINS", "AVG_SPEED", "MAX_SPEED", "DISTANCE_TRAVELED",
        "DISTANCE_TRAVELLED_ODOMETER", "MOVE_PERCENT", "MOVE_COUNT", "MOVE_COUNT_MINS",
        "MOVE_MINS", "IGN_ALERT_COUNT", "IGNITION_COUNT", "IGNITION_COUNT_MINS", "IGNITION_MINS",
        "NO_TRIPS_YARD", "NIGHT_STOP_MINS", "STOP_COUNT", "STOP_COUNT_MINS", "STOP_MINS",
        "STOP_ENGINE_HOURS", "OFFLINE_COUNT_MINS", "REGION_ID", "DEALER_ID", "PREVIOUS_ODOMETER",
        "END_ODOMETER", "START_ODOMETER", "SCORE_CARD"
    ],
    "zero_percentage": [
        99.95, 99.94, 99.93, 99.93, 99.92, 99.92, 99.91, 99.91, 99.91, 99.75, 99.75, 99.74, 99.73, 99.73,
        99.71, 99.70, 99.70, 99.47, 99.39, 99.09, 99.08, 97.76, 96.36, 96.00, 95.71, 95.71, 95.58, 94.02,
        92.49, 91.54, 82.79, 82.42, 79.97, 78.53, 69.26, 69.26, 66.57, 66.00, 61.48, 61.08, 60.63, 60.63,
        58.70, 53.46, 53.09, 52.11, 51.47, 40.64, 40.64, 40.63, 40.63, 39.38, 39.35, 39.27, 39.26, 38.71,
        38.71, 38.71, 38.71, 36.51, 36.33, 36.33, 36.29, 35.77, 31.55, 28.48, 28.48, 28.21, 27.74, 27.74,
        26.21, 26.21, 8.20, 8.20, 8.20, 0.30
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Ensure lengths match (The provided data lists might have a mismatch if copy-pasted incorrectly, but user provided explicit lists)
# Let's double check lengths just in case, though the user provided code implies they are correct.
if len(df["column"]) != len(df["zero_percentage"]):
    print(f"Warning: Length mismatch. Columns: {len(df['column'])}, Percentages: {len(df['zero_percentage'])}")
    # Truncate to shorter length to allow running if needed, or error out.
    min_len = min(len(df["column"]), len(df["zero_percentage"]))
    df = df.iloc[:min_len]

df = df.sort_values(by="zero_percentage", ascending=False)

# --- Normalize for heatmap color mapping ---
# Avoid division by zero if max == min
range_val = df["zero_percentage"].max() - df["zero_percentage"].min()
if range_val == 0:
    norm = np.zeros(len(df))
else:
    norm = (df["zero_percentage"] - df["zero_percentage"].min()) / range_val

# Use a smoother palette
try:
    cmap = sns.color_palette("RdYlGn_r", 256)
except Exception as e:
    print(f"Error loading palette: {e}. Falling back to default.")
    cmap = plt.cm.RdYlGn_r

# --- Create figure ---
# Calculate figure height dynamically based on number of rows
fig_height = max(10, len(df) * 0.33)
plt.figure(figsize=(12, fig_height), dpi=300)

# Horizontal bars
# Note: In matplotlib, scatter or barh takes raw colors. cmap(int) works if cmap is a Colormap object.
# sns.color_palette returns a list of RGB tuples.
# We need to map the normalized value 'nval' (0-1) to an index (0-255).

for i, (col, val, nval) in enumerate(zip(df["column"], df["zero_percentage"], norm)):
    color_idx = int(nval * 255)
    # Clamp index just in case
    color_idx = max(0, min(color_idx, 255))

    # If using seaborn palette (list of tuples), access by index
    # If using matplotlib colormap (callable), call with nval
    if isinstance(cmap, list):
        bar_color = cmap[color_idx]
    else:
        bar_color = cmap(nval) # Logic for matplotlib colormap

    plt.barh(
        i, val,
        color=bar_color,
        height=0.6,
        alpha=0.9
    )

# Y-axis labels with bold text
plt.yticks(range(len(df)), df["column"], fontsize=9, fontweight="bold")

# Title and labels
plt.xlabel("Missingness (%)", fontsize=12)
plt.title("Missingness by Column (High-Resolution Heatmap Table)", fontsize=16, pad=20)

plt.xlim(0, 105) # Little extra space for text
plt.grid(axis="x", linestyle="--", alpha=0.3)

# Value labels
for i, val in enumerate(df["zero_percentage"]):
    plt.text(val + 1.0, i, f"{val:.2f}%", fontsize=8, va='center')

plt.gca().invert_yaxis()
plt.tight_layout()

# Save high-resolution image
output_file = "missingness_heatmap.png"
plt.savefig(output_file, dpi=300, bbox_inches="tight")
print(f"Plot saved to {output_file}")

# plt.show() # Disabled for headless environment
