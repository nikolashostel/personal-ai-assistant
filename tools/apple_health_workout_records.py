from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path

RUNNING = "HKWorkoutActivityTypeRunning"
INTERESTING = {
    "HKQuantityTypeIdentifierDistanceWalkingRunning",
    "HKQuantityTypeIdentifierHeartRate",
    "HKQuantityTypeIdentifierStepCount",
    "HKQuantityTypeIdentifierRunningSpeed",
    "HKQuantityTypeIdentifierRunningStrideLength",
    "HKQuantityTypeIdentifierFlightsClimbed",
    "HKQuantityTypeIdentifierElevationAscended",
    "HKQuantityTypeIdentifierActiveEnergyBurned",
}


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect Apple Health records around running workouts"
    )
    parser.add_argument("--file", default="data/apple_health/export.xml")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument(
        "--window", type=int, default=60, help="minutes around workout start/end"
    )
    parser.add_argument(
        "--year", type=int, help="select running workouts from a specific year"
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    workouts: list[dict] = []
    for event, elem in ET.iterparse(path, events=("end",)):
        if elem.tag == "Workout" and elem.attrib.get("workoutActivityType") == RUNNING:
            workout = dict(elem.attrib)
            if args.year is None or parse_date(workout["startDate"]).year == args.year:
                workouts.append(workout)
                if len(workouts) >= args.limit:
                    break
        elem.clear()

    print("Apple Health running workout record inspector")
    print("=" * 48)
    print(f"File: {path}")
    if args.year is not None:
        print(f"Year filter: {args.year}")
    print(f"Selected running workouts: {len(workouts)}")

    if not workouts:
        return

    selected = []
    for i, workout in enumerate(workouts, 1):
        start = parse_date(workout["startDate"])
        end = parse_date(workout["endDate"])
        selected.append((i, start, end, workout))

    records_by_workout: dict[int, dict[str, list[dict]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for event, elem in ET.iterparse(path, events=("end",)):
        if elem.tag == "Record":
            attrs = elem.attrib
            record_type = attrs.get("type")
            if record_type in INTERESTING:
                try:
                    start = parse_date(attrs["startDate"])
                    end = parse_date(attrs["endDate"])
                except (KeyError, ValueError):
                    elem.clear()
                    continue

                for index, workout_start, workout_end, _ in selected:
                    if end >= workout_start and start <= workout_end:
                        records_by_workout[index][record_type].append(attrs)
            elem.clear()

    for index, start, end, workout in selected:
        print(f"\n[{index}]")
        print(f"Start: {workout.get('startDate')}")
        print(f"End:   {workout.get('endDate')}")
        print(f"Duration: {workout.get('duration')} {workout.get('durationUnit')}")
        print(f"Source: {workout.get('sourceName')}")
        print("\nOverlapping records:")

        groups = records_by_workout[index]
        if not groups:
            print("  NONE")
            continue

        for record_type, records in sorted(groups.items()):
            values = []
            for record in records:
                try:
                    values.append(float(record["value"]))
                except (KeyError, ValueError):
                    pass
            print(f"\n  {record_type}")
            print(f"    count: {len(records)}")
            if values:
                print(f"    unit: {records[0].get('unit')}")
                print(f"    min: {min(values):g}")
                print(f"    max: {max(values):g}")
                print(f"    avg: {sum(values) / len(values):g}")
            else:
                print("    numeric values: none")


if __name__ == "__main__":
    main()
