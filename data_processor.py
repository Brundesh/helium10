"""
Data processing module for Helium 10 Xray CSV files.
Handles CSV parsing, data cleaning, and deduplication.
"""

import pandas as pd
import re
from typing import Dict, Any, Optional


def clean_numeric_value(value: Any) -> float:
    """
    Clean numeric values by removing commas, currency symbols, and handling N/A.

    Args:
        value: Raw value from CSV (string, int, or float)

    Returns:
        Cleaned float value or 0.0 if invalid
    """
    try:
        # Check for NaN first using try-except to handle Series
        if pd.isna(value):
            return 0.0
    except (ValueError, TypeError):
        # If pd.isna fails on a Series, skip this check
        pass

    # Check for None
    if value is None:
        return 0.0

    # Check for string N/A values
    if isinstance(value, str):
        stripped = value.strip()
        if stripped in ['N/A', 'NA', '', 'n/a', 'na']:
            return 0.0

    # If already numeric, return as float
    if isinstance(value, (int, float)):
        return float(value)

    # Convert to string and remove currency symbols, commas, and spaces
    cleaned = str(value).replace('₹', '').replace(',', '').replace(' ', '').strip()

    # Check if empty after cleaning
    if not cleaned or cleaned in ['N/A', 'NA', 'n/a', 'na']:
        return 0.0

    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def load_and_clean_csv(file) -> pd.DataFrame:
    """
    Load CSV file and clean the data.

    Args:
        file: Uploaded file object from Streamlit

    Returns:
        Cleaned DataFrame

    Raises:
        ValueError: If required columns are missing
    """
    # Required columns (case-insensitive matching)
    required_columns = ['ASIN', 'Brand', 'Price', 'Revenue', 'Sales', 'Review Count', 'Ratings']

    try:
        # Read CSV with UTF-8 encoding (handles BOM automatically)
        df = pd.read_csv(file, encoding='utf-8-sig')

        # Normalize column names (handle variations like "Price  ₹")
        df.columns = df.columns.str.strip()

        # Create column mapping for variations
        # Be specific to avoid mapping multiple columns to the same name
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()

            # Handle "Price  ₹" or similar variations (but not "Unit Price", etc.)
            if col_lower.startswith('price') or col_lower == 'price  ₹':
                column_mapping[col] = 'Price'
            # Revenue (exact match or starts with)
            elif col_lower == 'revenue' or (col_lower.startswith('revenue') and 'monthly' not in col_lower):
                column_mapping[col] = 'Revenue'
            # Sales - must be exact or just "Sales", not "Variation Sales"
            elif col_lower == 'sales':
                column_mapping[col] = 'Sales'
            # Review Count
            elif 'review count' in col_lower or col_lower == 'reviews':
                column_mapping[col] = 'Review Count'
            # Ratings
            elif col_lower == 'ratings' or col_lower == 'rating':
                column_mapping[col] = 'Ratings'
            # ASIN
            elif col_lower == 'asin':
                column_mapping[col] = 'ASIN'
            # Brand
            elif col_lower == 'brand':
                column_mapping[col] = 'Brand'
            # Product Details
            elif 'product details' in col_lower or col_lower == 'title':
                column_mapping[col] = 'Product Details'

        # Rename columns
        df = df.rename(columns=column_mapping)

        # Check for required columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

        # Clean numeric columns
        df['Price'] = df['Price'].apply(clean_numeric_value)
        df['Revenue'] = df['Revenue'].apply(clean_numeric_value)
        df['Sales'] = df['Sales'].apply(clean_numeric_value)
        df['Review Count'] = df['Review Count'].apply(clean_numeric_value)
        df['Ratings'] = df['Ratings'].apply(clean_numeric_value)

        # Remove rows with zero or invalid revenue (likely invalid data)
        # Use .loc to avoid SettingWithCopyWarning
        df = df.loc[df['Revenue'] > 0].copy()

        # Remove duplicates by ASIN (keep first occurrence)
        df = df.drop_duplicates(subset=['ASIN'], keep='first')

        # Sort by revenue (descending)
        df = df.sort_values('Revenue', ascending=False).reset_index(drop=True)

        return df

    except ValueError as ve:
        # Re-raise ValueError with original message
        raise ve
    except Exception as e:
        # Provide more helpful error message for other exceptions
        import traceback
        error_details = traceback.format_exc()
        raise ValueError(f"Error processing CSV file: {str(e)}\n\nDetails: Check that your CSV has the required columns and valid data.")


def get_top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Get top N products by revenue.

    Args:
        df: Cleaned DataFrame
        n: Number of top products to return

    Returns:
        DataFrame with top N products
    """
    return df.head(n).copy()


def validate_dataframe(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """
    Validate that DataFrame has required structure and data.

    Args:
        df: DataFrame to validate

    Returns:
        Tuple of (is_valid, list of warning messages)
    """
    warnings = []

    if df is None or len(df) == 0:
        return False, ["X-Ray data is empty"]

    required_cols = ['ASIN', 'Brand', 'Price', 'Revenue', 'Sales', 'Review Count', 'Ratings']

    for col in required_cols:
        if col not in df.columns:
            return False, [f"Missing required column: {col}"]

    # Data quality checks
    if len(df) < 10:
        warnings.append(f"Only {len(df)} products found - export may be incomplete (expected 10+)")

    # Check for suspicious data
    zero_revenue_count = (df['Revenue'] == 0).sum()
    if zero_revenue_count > 0:
        warnings.append(f"{zero_revenue_count} products with zero revenue (filtered out)")

    # Check price range
    max_price = df['Price'].max()
    if max_price > 50000:
        warnings.append(f"Some products have very high prices (max: ₹{max_price:,.0f})")

    min_price = df[df['Price'] > 0]['Price'].min() if (df['Price'] > 0).any() else 0
    if min_price < 50 and min_price > 0:
        warnings.append(f"Some products have very low prices (min: ₹{min_price:,.0f})")

    return True, warnings
