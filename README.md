# Task 5 — Environmental Sensor Data Dashboard

A static dashboard (`index.html`) that reads sensor readings from `sensor_data.json`.
`generate_sensor_data.py` produces that JSON (and a CSV copy) from a small fake
data model — three stations, each with temperature, humidity, pressure, air
quality, light intensity, and GPS position, plus the last 5 readings per sensor.

## Files

- `index.html` — the dashboard. No sensor values are hardcoded in it; it fetches `sensor_data.json` at load time.
- `generate_sensor_data.py` — generates `sensor_data.json` and `sensor_data.csv`.
- `sensor_data.json` / `sensor_data.csv` — the current dataset (already generated; regenerate any time).

## Regenerating the dataset

```bash
python generate_sensor_data.py            # writes sensor_data.json/.csv in this folder
python generate_sensor_data.py --seed 7   # reproducible run
```

Re-run this, then refresh the page — no HTML/JS changes needed.

## Viewing it locally

Browsers block `fetch()` of local files opened directly (`file://...`), so
don't just double-click `index.html`. Serve the folder instead:

```bash
python -m http.server 8000
```

then open `http://localhost:8000` in a browser.

## Publishing to GitHub Pages

1. Put `index.html`, `sensor_data.json`, and (optionally) `generate_sensor_data.py` in your repo — e.g. a `docs/` folder or the repo root.
2. In the repo settings, enable GitHub Pages for that folder/branch.
3. GitHub Pages serves everything over HTTP, so the `fetch('sensor_data.json')` call works the same way it does with the local server above — no code changes needed.

## Swapping in real sensor data later

The dashboard only cares about the JSON shape `generate_sensor_data.py`
produces: a `stations` object keyed by station ID, each with `name`, `gps`,
and a `sensors` object (each sensor has `value`, `unit`, and a 5-item
`history` array). Point any real data export at that same shape — from your
ESP32-D aggregator, a logging script, etc. — and `index.html` doesn't need
to change at all.
