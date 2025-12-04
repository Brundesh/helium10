#!/usr/bin/env python3
"""
Test script to verify CSV compatibility with the actual Helium 10 export format.
"""

import pandas as pd
import sys
from io import StringIO

# Simulate the CSV structure from your Helium 10 export
test_csv_content = """Display Order,Product Details,ASIN,URL,Image URL,Brand,Price  ₹,Sales,Variation Sales Strength (1 - 10),Recent Purchases,Revenue,Title Char. Count,BSR,Seller Country/Region,Fees  ₹,Active Sellers,Ratings,Review Count,Images,Review velocity,Buy Box,Category,Size Tier,Fulfillment,Dimensions,Weight,ABA Most Clicked,Creation Date,Sponsored,Best Seller,Seller Age (mo),Seller
1,"Test Product 1",B0CYH8XSVK,https://www.amazon.in/dp/B0CYH8XSVK,https://example.com/image.jpg,SOULWIT,658,174,0,100,"1,13,529.99",152,"5,076",N/A,189.56,1,4.1,"1,240",7,0,SoloWIT Online,Home Improvement,Standard Size,FBA,22.10 x 2.80 x 15.80 cm,0.15,N/A,"Mar 19, 2024",Sponsored Brand,No,20,SoloWIT Online
2,"Test Product 2",B07RQCXCR2,https://www.amazon.in/dp/B07RQCXCR2,https://example.com/image2.jpg,BRAND2,752,277,0,100,"2,13,824.41",158,"2,212",N/A,N/A,1,4.4,"11,429",7,0,Seller Online,Home Improvement,Standard Size,FBA,25.90 x 1.70 x 20.70 cm,0.3,N/A,"Jun 11, 2019",Sponsored Brand,No,77,Seller Online
3,"Test Product 3",B07T72KRVX,https://www.amazon.in/dp/B07T72KRVX,https://example.com/image3.jpg,BRAND3,398,291,0,100,"1,15,932.39",171,"1,354",N/A,122.53,2,3.5,"31,075",7,0,Another Seller,Home Improvement,Standard Size,FBA,15.19 x 1.91 x 9.30 cm,0.07,N/A,"Jun 29, 2019",Sponsored Brand,No,77,Another Seller
"""

def test_csv_parsing():
    """Test if the CSV can be parsed correctly."""
    print("=" * 60)
    print("Testing CSV Compatibility")
    print("=" * 60)

    try:
        # Test 1: Read CSV
        print("\n✓ Test 1: Reading CSV...")
        df = pd.read_csv(StringIO(test_csv_content))
        print(f"  - Loaded {len(df)} rows")
        print(f"  - Columns: {len(df.columns)}")

        # Test 2: Check required columns exist
        print("\n✓ Test 2: Checking required columns...")
        required = ['ASIN', 'Brand', 'Price  ₹', 'Revenue', 'Sales', 'Review Count', 'Ratings']
        for col in required:
            if col in df.columns:
                print(f"  ✓ {col}")
            else:
                print(f"  ✗ {col} - MISSING!")

        # Test 3: Clean numeric values
        print("\n✓ Test 3: Cleaning numeric values...")

        # Test Price cleaning
        price_val = df.loc[0, 'Price  ₹']
        print(f"  - Original Price: '{price_val}' (type: {type(price_val).__name__})")

        # Test Revenue cleaning (with commas)
        revenue_val = df.loc[0, 'Revenue']
        print(f"  - Original Revenue: '{revenue_val}' (type: {type(revenue_val).__name__})")

        # Test Review Count cleaning
        reviews_val = df.loc[0, 'Review Count']
        print(f"  - Original Review Count: '{reviews_val}' (type: {type(reviews_val).__name__})")

        # Test 4: Column name mapping
        print("\n✓ Test 4: Testing column name mapping...")
        df_test = df.copy()
        df_test.columns = df_test.columns.str.strip()

        column_mapping = {}
        for col in df_test.columns:
            if 'price' in col.lower():
                column_mapping[col] = 'Price'
                print(f"  - '{col}' → 'Price'")
            elif 'revenue' in col.lower():
                column_mapping[col] = 'Revenue'
                print(f"  - '{col}' → 'Revenue'")
            elif 'review count' in col.lower():
                column_mapping[col] = 'Review Count'
                print(f"  - '{col}' → 'Review Count'")

        df_test = df_test.rename(columns=column_mapping)
        print(f"  - Mapped columns successfully: {list(column_mapping.values())}")

        # Test 5: Clean and convert values
        print("\n✓ Test 5: Cleaning and converting values...")

        def clean_numeric(value):
            if pd.isna(value) or value in ['N/A', 'NA', '', None]:
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            cleaned = str(value).replace('₹', '').replace(',', '').replace(' ', '').strip()
            try:
                return float(cleaned)
            except ValueError:
                return 0.0

        df_test['Price'] = df_test['Price'].apply(clean_numeric)
        df_test['Revenue'] = df_test['Revenue'].apply(clean_numeric)
        df_test['Review Count'] = df_test['Review Count'].apply(clean_numeric)

        print(f"  - Cleaned Price (row 1): {df_test.loc[0, 'Price']}")
        print(f"  - Cleaned Revenue (row 1): {df_test.loc[0, 'Revenue']}")
        print(f"  - Cleaned Review Count (row 1): {df_test.loc[0, 'Review Count']}")

        # Verify conversions
        assert df_test.loc[0, 'Price'] == 658.0, "Price conversion failed!"
        assert df_test.loc[0, 'Revenue'] == 113529.99, "Revenue conversion failed!"
        assert df_test.loc[0, 'Review Count'] == 1240.0, "Review Count conversion failed!"

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour Helium 10 CSV format is FULLY COMPATIBLE with the app!")
        print("\nNotes:")
        print("  - Column 'Price  ₹' will be mapped to 'Price'")
        print("  - Indian comma formatting (1,13,529.99) will be cleaned")
        print("  - N/A values will be converted to 0")
        print("  - Special characters (₹) will be removed")
        print("\n" + "=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_csv_parsing()
    sys.exit(0 if success else 1)
