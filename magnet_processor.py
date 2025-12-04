"""
Magnet data processing module for Helium 10 Magnet CSV files.
Handles demand analysis, keyword metrics, and demand-supply calculations.
"""

import pandas as pd
import re
from typing import Dict, Any, List, Optional


def clean_numeric_with_commas(value: Any) -> int:
    """
    Clean numeric values that may have commas (e.g., "180,045" → 180045).

    Args:
        value: Raw value from CSV (string, int, or float)

    Returns:
        Cleaned integer value or 0 if invalid
    """
    try:
        if pd.isna(value):
            return 0
    except (ValueError, TypeError):
        pass

    if value is None:
        return 0

    if isinstance(value, str):
        stripped = value.strip()
        if stripped in ['N/A', 'NA', '', 'n/a', 'na']:
            return 0

    if isinstance(value, (int, float)):
        return int(value)

    # Remove commas and convert to int
    cleaned = str(value).replace(',', '').strip()

    if not cleaned or cleaned in ['N/A', 'NA', 'n/a', 'na']:
        return 0

    try:
        return int(float(cleaned))
    except (ValueError, TypeError):
        return 0


def clean_competing_products(value: str) -> int:
    """
    Convert competing product ranges to approximate integers.

    Examples:
        ">20,000" → 20000
        ">9,000" → 9000
        "520" → 520
        ">30,000" → 30000
        ">-2" → 0 (invalid data)

    Args:
        value: Raw competing products value

    Returns:
        Integer value
    """
    try:
        if pd.isna(value):
            return 0
    except (ValueError, TypeError):
        pass

    if value is None or value == '':
        return 0

    # Convert to string and clean
    value_str = str(value).strip()

    # Remove ">" prefix and commas
    cleaned = value_str.replace('>', '').replace(',', '').strip()

    if not cleaned or cleaned in ['N/A', 'NA', 'n/a', 'na']:
        return 0

    try:
        result = int(float(cleaned))
        # Return 0 for negative or very small values (invalid data)
        return max(0, result)
    except (ValueError, TypeError):
        return 0


def clean_trend_percentage(value: Any) -> float:
    """
    Clean trend percentage values.

    Examples:
        42 → 42.0
        -10 → -10.0
        "n/a" → 0.0

    Args:
        value: Raw trend value

    Returns:
        Float percentage value
    """
    try:
        if pd.isna(value):
            return 0.0
    except (ValueError, TypeError):
        pass

    if value is None:
        return 0.0

    if isinstance(value, str):
        stripped = value.strip()
        if stripped in ['N/A', 'NA', '', 'n/a', 'na']:
            return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    try:
        return float(str(value).replace(',', '').strip())
    except (ValueError, TypeError):
        return 0.0


def extract_seed_keyword_from_filename(filename: str) -> Optional[str]:
    """
    Extract seed keyword from Magnet CSV filename.

    Examples:
        "IN_AMAZON_magnet__2025-12-04_yoga mat.csv" → "yoga mat"
        "magnet_laptop_stand.csv" → "laptop stand"
        "spice rack organizer.csv" → "spice rack organizer"

    Args:
        filename: CSV filename

    Returns:
        Extracted keyword or None
    """
    # Remove .csv extension
    name = filename.replace('.csv', '')

    # Pattern 1: IN_AMAZON_magnet__DATE_keyword
    match = re.search(r'IN_AMAZON_magnet__\d{4}-\d{2}-\d{2}_(.+)$', name)
    if match:
        return match.group(1).strip()

    # Pattern 2: magnet_keyword
    match = re.search(r'magnet_(.+)$', name, re.IGNORECASE)
    if match:
        return match.group(1).replace('_', ' ').strip()

    # Pattern 3: Just the keyword (fallback)
    # Remove common prefixes
    for prefix in ['IN_AMAZON_magnet__', 'magnet_', 'magnet-']:
        if name.startswith(prefix):
            name = name[len(prefix):]

    # Replace underscores with spaces
    return name.replace('_', ' ').strip()


def parse_magnet_csv(file, filename: str = None) -> pd.DataFrame:
    """
    Parse Magnet CSV export.

    Handles:
    - BOM removal (file starts with ﻿)
    - Comma stripping from numeric columns
    - Competing products range conversion
    - Null value handling

    Args:
        file: Uploaded file object
        filename: Optional filename for reference

    Returns:
        Cleaned DataFrame with standardized columns
    """
    try:
        # Read CSV with UTF-8-SIG encoding (handles BOM)
        df = pd.read_csv(file, encoding='utf-8-sig')

        # Clean column names
        df.columns = df.columns.str.strip()

        # Verify required columns exist
        required_cols = ['Keyword Phrase', 'Search Volume', 'Search Volume Trend',
                        'Competing Products', 'Magnet IQ Score']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

        # Clean numeric columns
        df['Search Volume'] = df['Search Volume'].apply(clean_numeric_with_commas)
        df['Search Volume Trend'] = df['Search Volume Trend'].apply(clean_trend_percentage)
        df['Magnet IQ Score'] = df['Magnet IQ Score'].apply(clean_numeric_with_commas)
        df['Competing Products'] = df['Competing Products'].apply(clean_competing_products)

        # Clean CPR if it exists
        if 'CPR' in df.columns:
            df['CPR'] = df['CPR'].apply(clean_numeric_with_commas)

        # Clean keyword phrases
        df['Keyword Phrase'] = df['Keyword Phrase'].str.strip()

        # Remove rows with zero search volume (invalid data)
        df = df[df['Search Volume'] > 0].copy()

        # Sort by search volume descending
        df = df.sort_values('Search Volume', ascending=False).reset_index(drop=True)

        return df

    except Exception as e:
        raise ValueError(f"Error parsing Magnet CSV: {str(e)}")


def find_seed_keyword_row(df: pd.DataFrame, seed_keyword: str) -> Optional[pd.Series]:
    """
    Find the row containing the seed keyword (case-insensitive, flexible matching).

    Args:
        df: Magnet DataFrame
        seed_keyword: Seed keyword to search for

    Returns:
        Row as Series or None if not found
    """
    if seed_keyword is None:
        return None

    seed_lower = seed_keyword.lower().strip()

    # Exact match first
    mask = df['Keyword Phrase'].str.lower().str.strip() == seed_lower
    matches = df[mask]
    if len(matches) > 0:
        return matches.iloc[0]

    # Try finding closest match (contains seed keyword)
    mask = df['Keyword Phrase'].str.lower().str.contains(seed_lower, na=False, regex=False)
    matches = df[mask]
    if len(matches) > 0:
        # Return the one with highest search volume
        return matches.iloc[0]

    return None


def calculate_demand_metrics(df: pd.DataFrame, filename: str = None,
                             seed_keyword: str = None) -> Dict[str, Any]:
    """
    Calculate demand metrics from Magnet data.

    Args:
        df: Cleaned Magnet DataFrame
        filename: Optional filename for seed keyword extraction
        seed_keyword: Optional explicit seed keyword

    Returns:
        Dictionary with demand metrics
    """
    if len(df) == 0:
        return None

    # Determine seed keyword
    if seed_keyword is None and filename:
        seed_keyword = extract_seed_keyword_from_filename(filename)

    # Find seed keyword row
    seed_row = None
    if seed_keyword:
        seed_row = find_seed_keyword_row(df, seed_keyword)

    # If no seed keyword found, use the top keyword by search volume
    if seed_row is None:
        seed_row = df.iloc[0]
        seed_keyword = seed_row['Keyword Phrase']

    # Extract seed keyword metrics
    search_volume = int(seed_row['Search Volume'])
    trend = float(seed_row['Search Volume Trend'])
    competing_products = int(seed_row['Competing Products'])
    magnet_iq_score = int(seed_row['Magnet IQ Score'])

    # Get top related keywords (top 5 by search volume, excluding seed)
    top_related = []
    for idx, row in df.head(10).iterrows():
        keyword = row['Keyword Phrase']
        # Skip if it's the seed keyword
        if keyword.lower().strip() == seed_keyword.lower().strip():
            continue

        top_related.append({
            'keyword': keyword,
            'volume': int(row['Search Volume']),
            'trend': float(row['Search Volume Trend']),
            'competitors': int(row['Competing Products'])
        })

        if len(top_related) >= 5:
            break

    return {
        'seed_keyword': seed_keyword,
        'search_volume': search_volume,
        'trend': trend,
        'competing_products': competing_products,
        'magnet_iq_score': magnet_iq_score,
        'total_related_keywords': len(df),
        'top_related_keywords': top_related
    }


def calculate_demand_supply_ratio(demand_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate demand-to-supply ratio and score.

    Args:
        demand_metrics: Dictionary from calculate_demand_metrics

    Returns:
        Dictionary with ratio, scores, verdict, and reasoning
    """
    if demand_metrics is None:
        return None

    search_volume = demand_metrics['search_volume']
    competing_products = demand_metrics['competing_products']

    # Calculate ratio (avoid division by zero)
    if competing_products > 0:
        ratio = search_volume / competing_products
    else:
        ratio = search_volume  # Assume 1 competitor if 0

    # Demand Score (0-25) based on search_volume
    if search_volume >= 150000:
        demand_score = 25
        demand_tier = "Excellent"
    elif search_volume >= 100000:
        demand_score = 22
        demand_tier = "Very High"
    elif search_volume >= 50000:
        demand_score = 20
        demand_tier = "High"
    elif search_volume >= 30000:
        demand_score = 17
        demand_tier = "Moderate-High"
    elif search_volume >= 15000:
        demand_score = 14
        demand_tier = "Moderate"
    elif search_volume >= 5000:
        demand_score = 10
        demand_tier = "Low-Moderate"
    else:
        demand_score = 5
        demand_tier = "Low"

    # Supply Score (0-25) based on competing_products
    if competing_products < 5000:
        supply_score = 25
        supply_tier = "Undersupplied"
    elif competing_products < 10000:
        supply_score = 20
        supply_tier = "Low Competition"
    elif competing_products < 15000:
        supply_score = 17
        supply_tier = "Moderate Competition"
    elif competing_products < 20000:
        supply_score = 14
        supply_tier = "Moderate-High Competition"
    elif competing_products < 30000:
        supply_score = 10
        supply_tier = "High Competition"
    else:
        supply_score = 7
        supply_tier = "Saturated"

    # Balance score
    balance_score = demand_score + supply_score

    # Verdict based on ratio
    if ratio >= 8.0:
        verdict = "EXCELLENT"
        verdict_color = "green"
        verdict_emoji = "🔥"
    elif ratio >= 4.0:
        verdict = "GOOD"
        verdict_color = "green"
        verdict_emoji = "✅"
    elif ratio >= 2.0:
        verdict = "MODERATE"
        verdict_color = "yellow"
        verdict_emoji = "⚠️"
    elif ratio >= 1.0:
        verdict = "POOR"
        verdict_color = "orange"
        verdict_emoji = "⚠️"
    else:
        verdict = "AVOID"
        verdict_color = "red"
        verdict_emoji = "❌"

    # Generate reasoning
    reasoning = f"With {search_volume:,} monthly searches and {competing_products:,} competing products, "
    reasoning += f"this keyword shows {demand_tier.lower()} demand in a {supply_tier.lower()} market. "
    reasoning += f"The ratio of {ratio:.1f} searches per competitor indicates a {verdict.lower()} opportunity."

    return {
        'ratio': ratio,
        'demand_score': demand_score,
        'supply_score': supply_score,
        'balance_score': balance_score,
        'demand_tier': demand_tier,
        'supply_tier': supply_tier,
        'verdict': verdict,
        'verdict_color': verdict_color,
        'verdict_emoji': verdict_emoji,
        'reasoning': reasoning
    }


def detect_trend_signal(trend: float) -> Dict[str, str]:
    """
    Classify trend direction and strength.

    Args:
        trend: Percentage trend value

    Returns:
        Dictionary with signal, color, and emoji
    """
    if trend > 30:
        return {
            'signal': 'STRONG_GROWTH',
            'color': 'green',
            'emoji': '🔥',
            'description': 'Rapidly growing market'
        }
    elif trend >= 10:
        return {
            'signal': 'GROWTH',
            'color': 'green',
            'emoji': '✅',
            'description': 'Growing market'
        }
    elif trend >= -5:
        return {
            'signal': 'STABLE',
            'color': 'green',
            'emoji': '✅',
            'description': 'Stable market'
        }
    elif trend >= -15:
        return {
            'signal': 'DECLINING',
            'color': 'orange',
            'emoji': '⚠️',
            'description': 'Declining market'
        }
    else:
        return {
            'signal': 'COLLAPSING',
            'color': 'red',
            'emoji': '❌',
            'description': 'Rapidly declining market'
        }


def validate_magnet_dataframe(df: pd.DataFrame) -> tuple[bool, List[str]]:
    """
    Validate Magnet DataFrame and generate quality warnings.

    Args:
        df: Magnet DataFrame

    Returns:
        Tuple of (is_valid, list of warning messages)
    """
    warnings = []

    if df is None or len(df) == 0:
        return False, ["Magnet data is empty"]

    # Check for minimum data quality
    if len(df) < 50:
        warnings.append(f"Only {len(df)} keywords found - export may be incomplete (expected 50+)")

    # Check if all search volumes are 0
    if df['Search Volume'].sum() == 0:
        warnings.append("All search volumes are 0 - invalid data")
        return False, warnings

    # Check for missing competing products data
    zero_competitors = (df['Competing Products'] == 0).sum()
    if zero_competitors > len(df) * 0.3:  # More than 30% missing
        warnings.append(f"{zero_competitors} keywords missing competitor data")

    return True, warnings
