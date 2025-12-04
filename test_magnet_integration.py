"""Quick test of Magnet integration with sample files."""

import sys
from magnet_processor import (
    parse_magnet_csv,
    calculate_demand_metrics,
    calculate_demand_supply_ratio,
    detect_trend_signal,
    validate_magnet_dataframe
)

def test_yoga_mat():
    """Test with yoga mat file."""
    print("=" * 60)
    print("Testing Yoga Mat CSV")
    print("=" * 60)

    file_path = "/mnt/c/Users/rbrun/Downloads/IN_AMAZON_magnet__2025-12-04_yoga mat.csv"
    filename = "IN_AMAZON_magnet__2025-12-04_yoga mat.csv"

    try:
        with open(file_path, 'rb') as f:
            df = parse_magnet_csv(f, filename)

        print(f"✅ Parsed CSV: {len(df)} keywords")

        # Validate
        is_valid, warnings = validate_magnet_dataframe(df)
        print(f"✅ Valid: {is_valid}")
        if warnings:
            for w in warnings:
                print(f"  ⚠️  {w}")

        # Calculate demand metrics
        demand = calculate_demand_metrics(df, filename)
        print(f"\n📊 Demand Metrics:")
        print(f"  Seed Keyword: {demand['seed_keyword']}")
        print(f"  Search Volume: {demand['search_volume']:,}")
        print(f"  Trend: {demand['trend']:+.0f}%")
        print(f"  Competing Products: {demand['competing_products']:,}")
        print(f"  Magnet IQ Score: {demand['magnet_iq_score']:,}")
        print(f"  Total Related Keywords: {demand['total_related_keywords']}")

        # Calculate D/S ratio
        ds = calculate_demand_supply_ratio(demand)
        print(f"\n💡 Demand/Supply Analysis:")
        print(f"  Ratio: {ds['ratio']:.2f}")
        print(f"  Demand Score: {ds['demand_score']}/25 ({ds['demand_tier']})")
        print(f"  Supply Score: {ds['supply_score']}/25 ({ds['supply_tier']})")
        print(f"  Balance Score: {ds['balance_score']}/50")
        print(f"  Verdict: {ds['verdict_emoji']} {ds['verdict']}")
        print(f"  Reasoning: {ds['reasoning']}")

        # Trend signal
        trend_signal = detect_trend_signal(demand['trend'])
        print(f"\n📈 Trend Signal:")
        print(f"  {trend_signal['emoji']} {trend_signal['signal']} - {trend_signal['description']}")

        print(f"\n✅ Test passed for yoga mat!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_laptop_stand():
    """Test with laptop stand file."""
    print("\n" + "=" * 60)
    print("Testing Laptop Stand CSV")
    print("=" * 60)

    file_path = "/mnt/c/Users/rbrun/Downloads/IN_AMAZON_magnet__2025-12-04_laptop stand.csv"
    filename = "IN_AMAZON_magnet__2025-12-04_laptop stand.csv"

    try:
        with open(file_path, 'rb') as f:
            df = parse_magnet_csv(f, filename)

        print(f"✅ Parsed CSV: {len(df)} keywords")

        demand = calculate_demand_metrics(df, filename)
        print(f"\n📊 Key Stats:")
        print(f"  Seed: {demand['seed_keyword']}")
        print(f"  Volume: {demand['search_volume']:,}")
        print(f"  Trend: {demand['trend']:+.0f}%")

        ds = calculate_demand_supply_ratio(demand)
        print(f"  D/S Ratio: {ds['ratio']:.2f} ({ds['verdict']})")

        print(f"\n✅ Test passed for laptop stand!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = True

    success = test_yoga_mat() and success
    success = test_laptop_stand() and success

    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
    print("=" * 60)
