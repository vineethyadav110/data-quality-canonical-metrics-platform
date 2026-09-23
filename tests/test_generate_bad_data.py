from ingestion.generate_bad_data import generate


def test_generator_creates_expected_defects() -> None:
    rows = generate(20, seed=42)
    assert len(rows) == 20
    assert rows[0]["distance_miles"] < 0
    assert rows[1]["vehicle_id"] == ""
    assert rows[2]["delivery_status"] == "completeed"
    assert rows[3]["fare_amount"] < 0
    assert rows[4]["completed_at"] == rows[4]["started_at"]
    assert rows[5]["trip_id"] == rows[6]["trip_id"]
