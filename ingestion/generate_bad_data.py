"""Generate synthetic mobility/delivery trip data with controlled defects."""
from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

STATUSES = ["completed", "cancelled", "in_progress"]
ZONES = ["north", "south", "east", "west", "central"]


def generate(rows: int, seed: int = 42) -> list[dict[str, object]]:
    rng = random.Random(seed)
    base = datetime(2026, 9, 1, 8, 0, tzinfo=timezone.utc)
    result: list[dict[str, object]] = []

    for i in range(rows):
        started = base + timedelta(minutes=rng.randint(0, 60 * 24 * 14))
        duration = rng.randint(240, 3600)
        completed = started + timedelta(seconds=duration)
        result.append(
            {
                "trip_id": f"T{i+1:06d}",
                "vehicle_id": f"V{rng.randint(1, 40):03d}",
                "started_at": started.isoformat(),
                "completed_at": completed.isoformat(),
                "pickup_zone": rng.choice(ZONES),
                "dropoff_zone": rng.choice(ZONES),
                "distance_miles": round(rng.uniform(0.5, 18.0), 2),
                "duration_seconds": duration,
                "delivery_status": rng.choice(STATUSES),
                "fare_amount": round(rng.uniform(4.0, 65.0), 2),
            }
        )

    # Controlled defects for the portfolio demo.
    if rows >= 6:
        result[0]["distance_miles"] = -4.7
        result[1]["vehicle_id"] = ""
        result[2]["delivery_status"] = "completeed"
        result[3]["fare_amount"] = -12.50
        result[4]["completed_at"] = result[4]["started_at"]
        result[5]["trip_id"] = result[6]["trip_id"]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--output", type=Path, default=Path("seeds/raw_trips.csv"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rows = generate(args.rows, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows):,} records to {args.output}")


if __name__ == "__main__":
    main()
