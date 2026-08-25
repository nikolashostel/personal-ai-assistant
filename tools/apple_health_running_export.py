from __future__ import annotations

import argparse
import copy
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

RUNNING = "HKWorkoutActivityTypeRunning"
INTERESTING_RECORDS = {
    "HKQuantityTypeIdentifierDistanceWalkingRunning",
    "HKQuantityTypeIdentifierHeartRate",
    "HKQuantityTypeIdentifierRunningSpeed",
    "HKQuantityTypeIdentifierRunningStrideLength",
    "HKQuantityTypeIdentifierStepCount",
    "HKQuantityTypeIdentifierElevationAscended",
    "HKQuantityTypeIdentifierFlightsClimbed",
    "HKQuantityTypeIdentifierActiveEnergyBurned",
}


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")


def overlaps(start: datetime, end: datetime, workout_start: datetime, workout_end: datetime) -> bool:
    return end >= workout_start and start <= workout_end


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a compact Apple Health XML containing only running workouts and related metrics"
    )
    parser.add_argument("--file", default="data/apple_health/export.xml")
    parser.add_argument(
        "--output", default="data/apple_health/running_export.xml"
    )
    args = parser.parse_args()

    source = Path(args.file)
    output = Path(args.output)
    if not source.exists():
        raise SystemExit(f"File not found: {source}")

    print("Apple Health running-only export")
    print("=" * 36)
    print(f"Source: {source}")
    print(f"Output: {output}")
    print("Finding running workouts...")

    workouts: list[dict[str, str]] = []
    for event, elem in ET.iterparse(source, events=("end",)):
        if elem.tag == "Workout" and elem.attrib.get("workoutActivityType") == RUNNING:
            workouts.append(dict(elem.attrib))
        elem.clear()

    if not workouts:
        raise SystemExit("No running workouts found")

    windows = [
        (parse_date(w["startDate"]), parse_date(w["endDate"]))
        for w in workouts
    ]

    print(f"Running workouts: {len(workouts)}")
    print("Collecting related records...")

    related_records: list[dict[str, str]] = []
    for event, elem in ET.iterparse(source, events=("end",)):
        if elem.tag == "Record":
            attrs = elem.attrib
            if attrs.get("type") not in INTERESTING_RECORDS:
                elem.clear()
                continue

            try:
                start = parse_date(attrs["startDate"])
                end = parse_date(attrs["endDate"])
            except (KeyError, ValueError):
                elem.clear()
                continue

            if any(overlaps(start, end, ws, we) for ws, we in windows):
                related_records.append(dict(attrs))
        elem.clear()

    print(f"Related records: {len(related_records)}")
    print("Writing compact XML...")

    root = ET.Element("HealthData")
    root.set("exportVersion", "running-only-1")
    root.set("sourceFile", source.name)
    root.set("generatedAt", datetime.now().astimezone().isoformat())

    workout_list = ET.SubElement(root, "Workouts")
    for workout in workouts:
        ET.SubElement(workout_list, "Workout", workout)

    record_list = ET.SubElement(root, "Records")
    for record in related_records:
        ET.SubElement(record_list, "Record", record)

    output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)

    size_mb = output.stat().st_size / (1024 * 1024)
    print("Done")
    print(f"Output size: {size_mb:.1f} MB")
    print(f"Workouts: {len(workouts)}")
    print(f"Records: {len(related_records)}")
    print(f"Saved to: {output}")


if __name__ == "__main__":
    main()
