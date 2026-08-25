from __future__ import annotations

import argparse
import statistics
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path

RUNNING = "HKWorkoutActivityTypeRunning"
METRICS = {
    "HKQuantityTypeIdentifierDistanceWalkingRunning": "distance",
    "HKQuantityTypeIdentifierHeartRate": "heart_rate",
    "HKQuantityTypeIdentifierRunningSpeed": "speed",
    "HKQuantityTypeIdentifierRunningStrideLength": "stride_length",
    "HKQuantityTypeIdentifierStepCount": "steps",
    "HKQuantityTypeIdentifierElevationAscended": "elevation",
}


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")


def overlaps(start: datetime, end: datetime, ws: datetime, we: datetime) -> bool:
    return end >= ws and start <= we


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect the latest Apple Health running workouts")
    parser.add_argument("--file", default="data/apple_health/running_export.xml")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    source = Path(args.file)
    root = ET.parse(source).getroot()

    workouts = [
        w for w in root.find("Workouts").findall("Workout")
        if w.attrib.get("workoutActivityType") == RUNNING
    ]
    workouts.sort(key=lambda w: parse_date(w.attrib["startDate"]), reverse=True)
    workouts = workouts[: args.limit]

    records = []
    for r in root.find("Records").findall("Record"):
        metric = METRICS.get(r.attrib.get("type", ""))
        if not metric:
            continue
        try:
            value = float(r.attrib["value"])
            start = parse_date(r.attrib["startDate"])
            end = parse_date(r.attrib["endDate"])
        except (KeyError, ValueError):
            continue
        records.append((metric, value, start, end, r.attrib))

    print("Apple Health — latest running workouts")
    print("=" * 55)
    print(f"File: {source}")
    print(f"Workouts analyzed: {len(workouts)}")

    for i, workout in enumerate(workouts, 1):
        a = workout.attrib
        ws, we = parse_date(a["startDate"]), parse_date(a["endDate"])
        duration = (we - ws).total_seconds()
        related = [r for r in records if overlaps(r[2], r[3], ws, we)]
        by_metric = defaultdict(list)
        for metric, value, start, end, attrs in related:
            by_metric[metric].append((value, start, end, attrs))

        print(f"\n[{i}] {a['startDate']}")
        print(f"  end:       {a['endDate']}")
        print(f"  duration:  {duration / 60:.1f} min")
        print(f"  source:    {a.get('sourceName', 'unknown')}")

        for metric in ("distance", "heart_rate", "speed", "stride_length", "steps", "elevation"):
            values = by_metric.get(metric, [])
            if not values:
                print(f"  {metric:14}: —")
                continue
            nums = [x[0] for x in values]
            units = values[0][3].get("unit", "")
            print(
                f"  {metric:14}: n={len(nums):4} "
                f"min={min(nums):.3f} max={max(nums):.3f} "
                f"avg={statistics.fmean(nums):.3f} {units}"
            )

        # Show the first/last distance and speed observations to reveal whether
        # Apple stores cumulative distance and instantaneous speed.
        for metric in ("distance", "speed"):
            values = sorted(by_metric.get(metric, []), key=lambda x: x[1])
            if values:
                first, last = values[0], values[-1]
                print(
                    f"  {metric:14} first={first[0]:.3f} at {first[1].strftime('%H:%M:%S')}"
                    f" | last={last[0]:.3f} at {last[1].strftime('%H:%M:%S')}"
                )

        # Print a compact time series for HR/speed, useful for identifying intervals.
        for metric in ("heart_rate", "speed"):
            values = sorted(by_metric.get(metric, []), key=lambda x: x[1])
            if values:
                sample = values[:8] + ([values[-1]] if len(values) > 8 else [])
                label = "HR" if metric == "heart_rate" else "SPD"
                print("  timeline", label + ":", ", ".join(
                    f"{x[1].strftime('%H:%M:%S')}={x[0]:.1f}" for x in sample
                ))

    print("\nNote: this is diagnostic output only; nothing is written to PostgreSQL.")


if __name__ == "__main__":
    main()
