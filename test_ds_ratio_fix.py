"""Test the D/S ratio fix with real data."""

from magnet_processor import calculate_demand_metrics, calculate_demand_supply_ratio
import pandas as pd

def test_yoga_mat_fixed():
    """Test yoga mat with FIXED D/S ratio using X-Ray product count."""

    print("=" * 70)
    print("TESTING YOGA MAT D/S RATIO FIX")
    print("=" * 70)

    # Simulate Magnet data
    magnet_demand = {
        'seed_keyword': 'yoga mat',
        'search_volume': 122840,
        'trend': 42,
        'competing_products': 30000,  # Magnet's broad count
        'magnet_iq_score': 4095
    }

    # Simulate X-Ray data (actual products ranking on pages 1-2)
    xray_metrics = {
        'total_products': 48  # This is the REAL competition
    }

    # Calculate D/S ratio with FIXED formula
    ds_result = calculate_demand_supply_ratio(magnet_demand, xray_metrics)

    print(f"\n📊 MAGNET DATA:")
    print(f"   Search Volume: {magnet_demand['search_volume']:,}/month")
    print(f"   Magnet Total Listings: {magnet_demand['competing_products']:,}")

    print(f"\n📦 X-RAY DATA (Pages 1-2):")
    print(f"   Products Ranking: {xray_metrics['total_products']}")

    print(f"\n🔥 CORRECTED D/S RATIO:")
    print(f"   Formula: {magnet_demand['search_volume']:,} ÷ {xray_metrics['total_products']} = {ds_result['ds_ratio']:.1f}")
    print(f"   Verdict: {ds_result['verdict_emoji']} {ds_result['verdict']}")
    print(f"   Success Rate: {ds_result['success_rate']:.2f}%")

    print(f"\n💡 INTERPRETATION:")
    print(f"   Each ranked product captures ~{ds_result['ds_ratio']:.0f} searches/month")
    print(f"   Only {ds_result['success_rate']:.2f}% of {magnet_demand['competing_products']:,} sellers rank")
    print(f"   {100 - ds_result['success_rate']:.1f}% of sellers FAILED to rank!")

    print(f"\n📝 REASONING:")
    print(f"   {ds_result['reasoning']}")

    print(f"\n✅ SCORES:")
    print(f"   Demand Score: {ds_result['demand_score']}/25 ({ds_result['demand_tier']})")
    print(f"   Supply Score: {ds_result['supply_score']}/25 ({ds_result['supply_tier']})")
    print(f"   Balance Score: {ds_result['balance_score']}/50")

    # Assert expected values
    expected_ratio = 122840 / 48
    assert abs(ds_result['ds_ratio'] - expected_ratio) < 1, f"D/S ratio should be ~{expected_ratio:.0f}"
    assert ds_result['verdict'] in ['GOLDMINE', 'EXCELLENT'], "Should be GOLDMINE or EXCELLENT"
    assert ds_result['success_rate'] < 0.2, "Success rate should be very low"

    print(f"\n✅ TEST PASSED!")
    return True


def test_laptop_stand_fixed():
    """Test laptop stand with FIXED D/S ratio."""

    print("\n" + "=" * 70)
    print("TESTING LAPTOP STAND D/S RATIO FIX")
    print("=" * 70)

    magnet_demand = {
        'seed_keyword': 'laptop stand',
        'search_volume': 180045,
        'trend': 2,
        'competing_products': 20000,
        'magnet_iq_score': 5000
    }

    xray_metrics = {
        'total_products': 47
    }

    ds_result = calculate_demand_supply_ratio(magnet_demand, xray_metrics)

    print(f"\n📊 D/S Ratio: {ds_result['ds_ratio']:.0f}")
    print(f"   Verdict: {ds_result['verdict_emoji']} {ds_result['verdict']}")
    print(f"   Success Rate: {ds_result['success_rate']:.2f}%")
    print(f"   Each product captures ~{ds_result['ds_ratio']:.0f} searches/month!")

    expected_ratio = 180045 / 47
    assert abs(ds_result['ds_ratio'] - expected_ratio) < 1
    assert ds_result['verdict'] in ['GOLDMINE', 'EXCELLENT']

    print(f"\n✅ TEST PASSED!")
    return True


def test_comparison_old_vs_new():
    """Compare old (WRONG) vs new (CORRECT) calculation."""

    print("\n" + "=" * 70)
    print("OLD vs NEW CALCULATION COMPARISON")
    print("=" * 70)

    search_volume = 180045
    magnet_total = 20000
    xray_count = 47

    old_ratio = search_volume / magnet_total
    new_ratio = search_volume / xray_count

    print(f"\nSearch Volume: {search_volume:,}/month")
    print(f"Magnet Total Listings: {magnet_total:,}")
    print(f"X-Ray Products (Pg 1-2): {xray_count}")

    print(f"\n❌ OLD (WRONG) Formula:")
    print(f"   {search_volume:,} ÷ {magnet_total:,} = {old_ratio:.1f}")
    print(f"   Verdict: Looks 'EXCELLENT' but understates by {new_ratio/old_ratio:.0f}x!")

    print(f"\n✅ NEW (CORRECT) Formula:")
    print(f"   {search_volume:,} ÷ {xray_count} = {new_ratio:.0f}")
    print(f"   Verdict: TRUE GOLDMINE! ({new_ratio:.0f} searches per ranked product)")

    print(f"\n🔥 IMPACT:")
    print(f"   Old formula understated opportunity by {new_ratio/old_ratio:.0f}x")
    print(f"   This changes {old_ratio:.1f} (good) → {new_ratio:.0f} (GOLDMINE!)")

    print(f"\n✅ COMPARISON COMPLETE!")
    return True


if __name__ == "__main__":
    success = True

    success = test_yoga_mat_fixed() and success
    success = test_laptop_stand_fixed() and success
    success = test_comparison_old_vs_new() and success

    print("\n" + "=" * 70)
    if success:
        print("✅ ALL TESTS PASSED - D/S RATIO FIX VERIFIED!")
    else:
        print("❌ SOME TESTS FAILED")
        exit(1)
    print("=" * 70)
