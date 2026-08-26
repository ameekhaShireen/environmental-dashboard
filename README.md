# Task 5 — Environmental Sensor Data Dashboard

A static dashboard (`index.html`) that reads sensor readings from `sensor_data.json`.
`generate_sensor_data.py` produces that JSON (and a CSV copy) from a small fake
data model — three stations, each with temperature, humidity, pressure, air
quality, light intensity, and GPS position, plus the last 5 readings per sensor.

## Files

- `index.html` — the dashboard. No sensor values are hardcoded in it; it fetches `sensor_data.json` at load time.
- `generate_sensor_data.py` — generates `sensor_data.json` and `sensor_data.csv`.
- `sensor_data.json` / `sensor_data.csv` — the current dataset (already generated; regenerate any time).

