"""
Dataset generator CLI entry point.
Run: python -m app.data.generate_dataset
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    t0 = time.time()
    print("=" * 60)
    print(" AI Logistics Platform — Synthetic Dataset Generator")
    print("=" * 60)

    try:
        from app.data.simulator import generate_all, OUTPUT_DIR
    except ImportError:
        # Allow running from backend/ directory
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from app.data.simulator import generate_all, OUTPUT_DIR

    # Parse CLI args for quick mode
    n_hist = 30000
    n_curr = 2000
    if "--quick" in sys.argv:
        n_hist = 5000
        n_curr = 500
        print("⚡ Quick mode: generating reduced dataset (5000 historical, 500 current)")

    datasets = generate_all(n_historical=n_hist, n_current=n_curr)

    elapsed = time.time() - t0
    print(f"\n⏱  Total time: {elapsed:.1f}s")
    print("\n📊 Summary:")
    for name, df in datasets.items():
        if hasattr(df, "__len__"):
            print(f"   {name:30s} {len(df):>8,} rows")

    print(f"\n📁 Files in {OUTPUT_DIR.resolve()}:")
    for f in sorted(OUTPUT_DIR.glob("*.csv")):
        size_kb = f.stat().st_size / 1024
        print(f"   {f.name:40s} {size_kb:8.0f} KB")

    print("\n✅ Done! Next steps:")
    print("   python -m app.data.validate_dataset")
    print("   python -m app.ml.train_model")
    print("   uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
