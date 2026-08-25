from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from pathlib import Path


RUNNING_TYPES = {
    "HKWorkoutActivityTypeRunning",
    "HKWorkoutActivityTypeRunningWorkout",
}


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d %H:%M:%S %Z"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Apple Health export.xml workouts without loading the whole file into memory.")
    parser.add_argument(
        "path",
        nargs="?",
        default="data/apple_health/export.xml",
        help="Path to Apple Health export.xml",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    total = 0
    running = 0
    types: Counter[str] = Counter()
    running_dates: list[datetime] = []
    samples: list[dict[str, str | None]] = []

    print("Apple Health export inspector")
    print("==============================")
    print(f"File: {path}")
    print(f"Size: {path.stat().st_size / 1024 / 1024:.1f} MB")
    print()
    print("Reading workouts...", flush=True)

    for event, elem in ET.iterparse(path, events=("end",)):
        if elem.tag != "Workout":
            continue

        total += 1
        workout_type = elem.attrib.get("workoutActivityType", "")
        types[workout_type] += 1

        if workout_type in RUNNING_TYPES or workout_type.lower().endswith("running"):
            running += 1
            start = elem.attrib.get("startDate")
            parsed = parse_date(start)
            if parsed:
                running_dates.append(parsed)

            if len(samples) < 5:
                samples.append(
                    {
                        "workoutActivityType": workout_type,
                        "startDate": start,
                        "endDate": elem.attrib.get("endDate"),
                        "duration": elem.attrib.get("duration"),
                        "durationUnit": elem.attrib.get("durationUnit"),
                        "totalDistance": elem.attrib.get("totalDistance"),
                        "totalDistanceUnit": elem.attrib.get("totalDistanceUnit"),
                        "totalEnergyBurned": elem.attrib.get("totalEnergyBurned"),
                        "totalEnergyBurnedUnit": elem.attrib.get("totalEnergyBurnedUnit"),
                        "sourceName": elem.attrib.get("sourceName"),
                    }
                )

        elem.clear()

    print()
    print(f"Total workouts: {total}")
    print(f"Running workouts: {running}")
    print()

    if running_dates:
        print(f"Running date range: {min(running_dates)} -> {max(running_dates)}")
        print()

    print("Workout activity types:")
    for workout_type, count in types.most_common():
        print(f"  {count:>5}  {workout_type}")

    print()
    print("Sample running workouts:")
    for index, sample in enumerate(samples, start=1):
        print(f"\n[{index}]")
        for key, value in sample.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
