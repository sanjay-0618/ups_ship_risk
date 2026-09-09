"""
Supabase Seeding Script — batch inserts all generated CSVs into Supabase.
Run: python -m app.data.seed_supabase
"""
from __future__ import annotations

import os
import sys
import math
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "generated"
BATCH_SIZE = 500


def _chunked(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def seed():
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "").strip()

    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment.")
        sys.exit(1)

    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)
        print(f"✅ Connected to Supabase: {supabase_url[:40]}...")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)

    # Verify tables exist before trying to seed
    try:
        client.table("locations").select("location_id").limit(1).execute()
    except Exception as e:
        err_str = str(e)
        if "PGRST205" in err_str or "Could not find the table" in err_str:
            print("\n❌ Table 'locations' does not exist in your Supabase database!")
            print("👉 You need to create the database tables first:")
            print("   1. Open Supabase Dashboard: https://supabase.com/dashboard/project/cbqnabhnjrbbyibyvmvv")
            print("   2. Go to 'SQL Editor' in the left menu.")
            print("   3. Paste the contents of 'database/schema.sql' and click 'Run'.")
            print("   4. Once the SQL runs successfully, re-run this command: py -m app.data.seed_supabase\n")
            sys.exit(1)

    def insert_table(table_name: str, csv_file: str, id_col: str | None = None):
        path = DATA_DIR / csv_file
        if not path.exists():
            print(f"  ⚠  {csv_file} not found — skipping")
            return 0

        df = pd.read_csv(path, low_memory=False)
        # Replace NaN with None for JSON compatibility
        df = df.where(pd.notna(df), None)
        records = df.to_dict(orient="records")

        # Check for existing data to avoid duplicates
        if id_col:
            try:
                existing = client.table(table_name).select(id_col).limit(1).execute()
                if existing.data:
                    print(f"  ⚠  {table_name} already has data — skipping (drop table first to re-seed)")
                    return 0
            except Exception:
                pass

        total = len(records)
        n_batches = math.ceil(total / BATCH_SIZE)
        inserted = 0

        print(f"  📤 {table_name}: {total:,} rows in {n_batches} batches", end="", flush=True)

        for batch in _chunked(records, BATCH_SIZE):
            try:
                # Remove internal private columns (prefixed with _)
                clean = [{k: v for k, v in r.items() if not k.startswith("_")} for r in batch]
                client.table(table_name).insert(clean).execute()
                inserted += len(batch)
                print(".", end="", flush=True)
            except Exception as e:
                print(f"\n    ❌ Batch error on {table_name}: {str(e)[:80]}")

        print(f" ✓ {inserted:,}/{total:,}")
        return inserted

    print("\n🚀 Starting Supabase seed...\n")

    # Insert in dependency order
    insert_table("locations", "locations.csv", "location_id")
    insert_table("route_edges", "route_edges.csv", "edge_id")
    insert_table("weather_events", "weather_events.csv", "event_id")
    insert_table("traffic_events", "traffic_events.csv", "event_id")
    insert_table("congestion_events", "congestion_events.csv", "event_id")
    insert_table("transport_events", "transport_events.csv", "transport_id")
    insert_table("external_events", "external_events.csv", "event_id")
    insert_table("historical_shipments", "historical_shipments.csv", "shipment_id")
    insert_table("shipment_events", "shipment_events.csv", "event_id")
    insert_table("historical_route_performance", "historical_route_performance.csv", "route_id")
    insert_table("shipments", "current_shipments.csv", "shipment_id")
    insert_table("risk_scores", "risk_scores.csv", "risk_id")

    print("\n✅ Seeding complete!")


if __name__ == "__main__":
    seed()
