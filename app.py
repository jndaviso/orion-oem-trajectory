import streamlit as st
import matplotlib.pyplot as plt
import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Orion OEM Trajectory", layout="centered")
st.title("Orion OEM Trajectory")

# Path to OEM file
file_path = "OEM - 2026.04.02 - post-USS-2 to EI.asc"

# Constants
earth_radius_km = 6378.137
local_tz = ZoneInfo("America/Edmonton")

# Storage
times_str = []
times_utc = []
x_vals = []
y_vals = []
z_vals = []
vx_vals = []
vy_vals = []
vz_vals = []

# -------------------------------
# Read OEM ephemeris data
# -------------------------------
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if not line:
            continue

        parts = line.split()

        # Ephemeris rows should have:
        # UTC, X, Y, Z, VX, VY, VZ
        if len(parts) != 7:
            continue

        # Skip non-data lines
        if "T" not in parts[0]:
            continue

        try:
            t_str = parts[0]
            t_utc = datetime.fromisoformat(t_str).replace(tzinfo=timezone.utc)

            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])
            vx = float(parts[4])
            vy = float(parts[5])
            vz = float(parts[6])

            times_str.append(t_str)
            times_utc.append(t_utc)
            x_vals.append(x)
            y_vals.append(y)
            z_vals.append(z)
            vx_vals.append(vx)
            vy_vals.append(vy)
            vz_vals.append(vz)

        except ValueError:
            continue

if not x_vals:
    raise ValueError("No ephemeris data rows were parsed from the file.")

# -------------------------------
# Current time and closest past state
# -------------------------------
now_utc = datetime.now(timezone.utc)
now_local = now_utc.astimezone(local_tz)

past_indices = [i for i, t in enumerate(times_utc) if t <= now_utc]

if not past_indices:
    raise ValueError("There are no state vectors at or before the current time.")

closest_past_idx = past_indices[-1]

closest_past_time_utc = times_utc[closest_past_idx]
closest_past_time_local = closest_past_time_utc.astimezone(local_tz)

closest_past_r = math.sqrt(
    x_vals[closest_past_idx]**2 +
    y_vals[closest_past_idx]**2 +
    z_vals[closest_past_idx]**2
)
closest_past_altitude = closest_past_r - earth_radius_km

speed_3d = math.sqrt(
    vx_vals[closest_past_idx]**2 +
    vy_vals[closest_past_idx]**2 +
    vz_vals[closest_past_idx]**2
)

radial_velocity = (
    x_vals[closest_past_idx] * vx_vals[closest_past_idx] +
    y_vals[closest_past_idx] * vy_vals[closest_past_idx] +
    z_vals[closest_past_idx] * vz_vals[closest_past_idx]
) / closest_past_r

tangential_velocity = math.sqrt(max(0.0, speed_3d**2 - radial_velocity**2))


# -------------------------------
# Split trajectory into past/future
# -------------------------------
past_x = [x_vals[i] for i in past_indices]
past_y = [y_vals[i] for i in past_indices]

future_x = [x_vals[i] for i in range(len(times_utc)) if times_utc[i] > now_utc]
future_y = [y_vals[i] for i in range(len(times_utc)) if times_utc[i] > now_utc]

# -------------------------------
# Build plot
# -------------------------------
fig, ax = plt.subplots(figsize=(8, 8))

# Past segment
if len(past_x) >= 2:
    ax.plot(past_x, past_y, linewidth=2, label="Past trajectory")
elif len(past_x) == 1:
    ax.scatter(past_x[0], past_y[0], s=20, label="Past trajectory")

# Future segment already present in OEM
if len(future_x) >= 2:
    ax.plot(future_x, future_y, color="#1f77b4", linestyle="--", linewidth=1, label="Future trajectory in OEM")
elif len(future_x) == 1:
    ax.scatter(future_x[0], future_y[0], s=20, label="Future trajectory in OEM")

# Start point of the OEM file
ax.scatter(x_vals[0], y_vals[0], color="orange", s=40, label="OEM start", zorder=5)

# Closest past state as directional triangle
back_steps = min(2, closest_past_idx)
forward_steps = min(2, len(x_vals) - 1 - closest_past_idx)

if back_steps >= 1 and forward_steps >= 1:
    i0 = closest_past_idx - back_steps
    i1 = closest_past_idx + forward_steps
    dx = x_vals[i1] - x_vals[i0]
    dy = y_vals[i1] - y_vals[i0]
elif forward_steps >= 1:
    i1 = closest_past_idx + forward_steps
    dx = x_vals[i1] - x_vals[closest_past_idx]
    dy = y_vals[i1] - y_vals[closest_past_idx]
elif back_steps >= 1:
    i0 = closest_past_idx - back_steps
    dx = x_vals[closest_past_idx] - x_vals[i0]
    dy = y_vals[closest_past_idx] - y_vals[i0]
else:
    dx, dy = 1.0, 0.0

angle = math.degrees(math.atan2(dy, dx)) - 90

ax.scatter(
    x_vals[closest_past_idx],
    y_vals[closest_past_idx],
    marker=(3, 0, angle),
    s=80,
    color="red",
    label="Closest past state",
    zorder=6
)

# Earth at origin
ax.scatter([0], [0], marker="o", s=180, color="green", label="Earth", zorder=5)

# Info text
info_text = (
    #f"Local time: {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
    f"State local time: {closest_past_time_local.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
    f"State altitude: {closest_past_altitude:,.0f} km\n"
    f"Speed: {speed_3d:,.2f} km/s\n"
    f"Radial velocity: {radial_velocity:,.2f} km/s\n"
    f"Tangential velocity: {tangential_velocity:,.2f} km/s"
)

ax.text(
    0.02, 0.98,
    info_text,
    transform=ax.transAxes,
    ha="left",
    va="top",
    bbox=dict(facecolor="white", alpha=0.85, edgecolor="black")
)

# Labels and formatting
ax.set_xlabel("X (km)")
ax.set_ylabel("Y (km)")
ax.set_title("Orion OEM Trajectory")
fig.text(
    0.5, 0.01,
    "Trajectory shown in EME2000 / J2000 top-down (X-Y) view. "
    "Solid = up to current time, dashed = future states already present in OEM.",
    ha="center",
    va="bottom"
)

ax.axis("equal")
ax.grid(True)
ax.legend()

st.pyplot(fig)
