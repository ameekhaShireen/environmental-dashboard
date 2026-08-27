"""
Generates a realistic fake environmental sensor dataset for three ground
stations (temperature, humidity, pressure, air quality, light intensity,
GPS position), and writes it out as both JSON (consumed by the dashboard
webpage) and CSV (for inspection / reporting).
"""

import argparse
import csv
import json
import random
from datetime import datetime, timedelta, timezone


SENSOR_DEFS = {
    "temp":     {"unit": "°C",  "step": 0.6, "min": 8,    "max": 42,
                 "normal": (16, 32), "watch": [(10, 16), (32, 38)], "decimals": 1},
    "humidity": {"unit": "%",   "step": 1.2, "min": 10,   "max": 95,
                 "normal": (30, 70), "watch": [(20, 30), (70, 85)], "decimals": 1},
    "pressure": {"unit": "hPa", "step": 0.4, "min": 975,  "max": 1040,
                 "normal": (995, 1022), "watch": [(985, 995), (1022, 1030)], "decimals": 1},
    "aqi":      {"unit": "AQI", "step": 3,   "min": 5,    "max": 180,
                 "normal": (0, 50), "watch": [(50, 100)], "decimals": 0},
    "light":    {"unit": "klx", "step": 0.3, "min": 0.5,  "max": 12,
                 "normal": (1, 8), "watch": [(0.5, 1), (8, 10)], "decimals": 1},
}

# One station profile per status we want to demonstrate on the dashboard.
# "target" is where that station's *latest* reading should land for that
# sensor; the walk is generated backwards from there so history looks
# realistic leading up to it.
STATION_PROFILES = {
    "A": {
        "name": "Station A — Rooftop Node",
        "base_lat": 24.4539, "base_lon": 54.3773,
        "targets": {  # all comfortably normal
            "temp": 24.5, "humidity": 52, "pressure": 1012.5, "aqi": 38, "light": 5.2,
        },
    },
    "B": {
        "name": "Station B — Field Node",
        "base_lat": 24.2130, "base_lon": 54.6890,
        "targets": {  # air quality drifting into WATCH
            "temp": 29.3, "humidity": 64.5, "pressure": 1008.7, "aqi": 78, "light": 7.1,
        },
    },
    "C": {
        "name": "Station C — Coastal Node",
        "base_lat": 24.5135, "base_lon": 54.3773,
        "targets": {  # temperature in ALERT
            "temp": 39.8, "humidity": 31.2, "pressure": 1017.9, "aqi": 46, "light": 9.6,
        },
    },
}

HISTORY_LENGTH = 5
SAMPLE_INTERVAL_MINUTES = 15


def round_value(value: float, decimals: int) -> float:
    return round(value, decimals) if decimals > 0 else round(value)


def generate_history(target: float, step: float, min_v: float, max_v: float,
                      decimals: int, length: int = HISTORY_LENGTH):
    """
    Walk backwards from `target` with small random deltas so the sequence
    looks like a real, slightly noisy time series arriving at `target`.
    Returns the history in chronological order (oldest -> newest == target).
    """
    values = [target]
    current = target
    for _ in range(length - 1):
        current -= random.uniform(-step, step)
        current = min(max_v, max(min_v, current))
        values.append(current)
    values.reverse()
    values[-1] = target  # keep the exact intended "current" reading
    return [round_value(v, decimals) for v in values]


def generate_gps(base_lat: float, base_lon: float):
    lat = base_lat + random.uniform(-0.0015, 0.0015)
    lon = base_lon + random.uniform(-0.0015, 0.0015)
    fix = random.choices(["3D FIX", "2D FIX"], weights=[0.9, 0.1])[0]
    return {"lat": f"{lat:.4f}", "lon": f"{lon:.4f}", "fix": fix}


def generate_dataset(seed: int | None = None):
    if seed is not None:
        random.seed(seed)

    now = datetime.now(timezone.utc)
    stations_out = {}

    for station_id, profile in STATION_PROFILES.items():
        sensors_out = {}
        for key, target in profile["targets"].items():
            defn = SENSOR_DEFS[key]
            history = generate_history(
                target=target,
                step=defn["step"],
                min_v=defn["min"],
                max_v=defn["max"],
                decimals=defn["decimals"],
            )
            sensors_out[key] = {
                "value": history[-1],
                "unit": defn["unit"],
                "history": history,
            }

        stations_out[station_id] = {
            "name": profile["name"],
            "gps": generate_gps(profile["base_lat"], profile["base_lon"]),
            "sensors": sensors_out,
        }

    return {
        "generated_at": now.isoformat(),
        "sample_interval_minutes": SAMPLE_INTERVAL_MINUTES,
        "stations": stations_out,
    }


def write_json(dataset: dict, path: str):
    with open(path, "w") as f:
        json.dump(dataset, f, indent=2)


def write_csv(dataset: dict, path: str):
    """
    Long-format CSV: one row per (station, sensor, history index).
    Easier to drop into a spreadsheet or report than nested JSON.
    """
    generated_at = datetime.fromisoformat(dataset["generated_at"])
    interval = timedelta(minutes=dataset["sample_interval_minutes"])

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["station_id", "station_name", "sensor", "unit",
                          "reading_index", "timestamp_utc", "value"])
        for station_id, station in dataset["stations"].items():
            for sensor_key, sensor in station["sensors"].items():
                history = sensor["history"]
                n = len(history)
                for i, value in enumerate(history):
                    # oldest reading is (n-1) intervals before "now"
                    ts = generated_at - interval * (n - 1 - i)
                    writer.writerow([
                        station_id, station["name"], sensor_key, sensor["unit"],
                        i, ts.isoformat(), value
                    ])


def main():
    parser = argparse.ArgumentParser(description="Generate fake environmental sensor data.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible output.")
    parser.add_argument("--out-dir", type=str, default=".", help="Directory to write sensor_data.json/.csv into.")
    args = parser.parse_args()

    dataset = generate_dataset(seed=args.seed)

    json_path = f"{args.out_dir}/sensor_data.json"
    csv_path = f"{args.out_dir}/sensor_data.csv"
    write_json(dataset, json_path)
    write_csv(dataset, csv_path)

    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")


if __name__ == "__main__":
    main()
