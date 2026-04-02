# Orion OEM Trajectory Viewer

A small Streamlit app that visualizes NASA Orion CCSDS OEM ephemeris data in a top-down EME2000 / J2000 X-Y view.

## What it shows

- Past trajectory up to the current time
- Future trajectory already present in the OEM file
- OEM start point
- Earth at the origin
- A directional marker for the closest past state
- State local time, altitude, speed, radial velocity, and tangential velocity

## Files

- `app.py` — Streamlit app
- `requirements.txt` — Python dependencies
- `OEM - 2026.04.02 - post-USS-2 to EI.asc` — ephemeris data file

## Notes

- The trajectory is shown in the EME2000 / J2000 inertial frame.
- This app uses the timestamps already present in the OEM file.
- The dashed trajectory is not predicted by the app; it is the future portion already included in the OEM.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py