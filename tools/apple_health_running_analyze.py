from __future__ import annotations

import argparse
import statistics
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
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
    "HKQuantityTypeIdentifierFlightsClimbed": "flights",
    "HKQuantityTypeIdentifierActiveEnergyBurned": "energy",
}


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")


def overlap(start: datetime, end: datetime, ws: datetime, we: datetime) -> bool:
    return end >= ws and start <= we


def to_float(value: str | None) -> float | None:
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze compact Apple Health running export")
    parser.add_argument("--file", default="data/apple_health/running_export.xml")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--all", action="store_true", help="Print all workouts")
    args = parser.parse_args()

    source = Path(args.file)
    if not source.exists():
        raise SystemExit(f"File not found: {source}")

    workouts: list[dict] = []
    records: list[dict] = []
    root = ET.parse(source).getroot()

    workout_node = root.find("Workouts")
    if workout_node is not None:
        for elem in workout_node.findall("Workout"):
            if elem.attrib.get("workoutActivityType") != RUNNING:
                continue
            attrs = elem.attrib
            workouts.append(
                {
                    "attrs": attrs,
                    "start": parse_date(attrs["startDate"]),
                    "end": parse_date(attrs["endDate"]),
                }
            )

    record_node = root.find("Records")
    if record_node is not None:
        for elem in record_node.findall("Record"):
            metric = METRICS.get(elem.attrib.get("type", ""))
            if metric:
                attrs = elem.attrib
                try:
                    start = parse_date(attrs["startDate"])
                    end = parse_date(attrs["endDate"])
                except (KeyError, ValueError):
                    continue
                value = to_float(attrs.get("value"))
                if value is not None:
                    records.append({"metric": metric, "attrs": attrs, "start": start, "end": end, "value": value})

    print("Apple Health running workout analyzer")
    print("=" * 40)
    print(f"File: {source}")
    print(f"Running workouts: {len(workouts)}")
    print(f"Selected metric records: {len(records)}")
    print()

    metric_counts = Counter(r["metric"] for r in records)
    print("Metric record counts:")
    for metric, count in metric_counts.most_common():
        print(f"  {metric:15} {count}")

    source_counts = Counter(w["attrs"].get("sourceName", "unknown") for w in workouts)
    print("\nWorkout sources:")
    for name, count in source_counts.most_common():
        print(f"  {count:3}  {name}")

    print("\nWorkout summaries:")
    selected = workouts if args.all else workouts[: args.limit]
    for index, workout in enumerate(selected, 1):
        attrs = workout["attrs"]
        ws, we = workout["start"], workout["end"]
        duration_sec = (we - ws).total_seconds()
        related = [r for r in records if overlap(r["start"], r["end"], ws, we)]
        by_metric: dict[str, list[dict]] = defaultdict(list)
        for record in related:
            by_metric[record["metric"]].append(record)

        print(f"\n[{index}] {ws:%Y-%m-%d %H:%M:%S %z}")
        print(f"  duration: {duration_sec / 60:.1f} min")
        print(f"  source:   {attrs.get('sourceName', 'unknown')}")
        print(f"  metadata: {attrs.get('metadata', '')}")

        for metric in sorted(by_metric):
            values = [r["value"] for r in by_metric[metric]]
            units = Counter(r["attrs"].get("unit", "") for r in by_metric[metric])
            unit = units.most_common(1)[0][0] if units else ""
            print(
                f"  {metric:15} count={len(values):4} "
                f"min={min(values):.3f} max={max(values):.3f} "
                f"avg={statistics.fmean(values):.3f} unit={unit}"
            )

        # Show any useful workout-level attributes without inventing semantics.
        ignored = {"workoutActivityType", "startDate", "endDate", "duration", "durationUnit"}
        extra = {k: v for k, v in attrs.items() if k not in ignored}
        print(f"  workout attributes: {extra}")

    print("\nImportant: these are raw overlapping-record statistics, not yet the final training metrics.")
    print("Next step is to determine the correct aggregation rules for distance, HR, speed, cadence/steps, elevation, and interval structure before importing into PostgreSQL.")


if __name__ == "__main__":
    main()
