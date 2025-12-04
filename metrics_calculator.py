"""
Metrics calculation module for Amazon FBA product opportunity analysis.
Calculates market size, concentration, pricing, and ratings metrics.
"""

import pandas as pd
from typing import Dict, Any, Tuple


def calculate_market_size(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate market size metrics.

    Args:
        df: Cleaned DataFrame sorted by revenue

    Returns:
        Dictionary with market size metrics
    """
    top_10_revenue = df.head(10)['Revenue'].sum()
    top_20_revenue = df.head(20)['Revenue'].sum()
    estimated_total_market = top_20_revenue * 2

    return {
        'top_10_revenue': top_10_revenue,
        'top_20_revenue': top_20_revenue,
        'estimated_total_market': estimated_total_market
    }


def calculate_market_concentration(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate market concentration metrics.

    Args:
        df: Cleaned DataFrame sorted by revenue

    Returns:
        Dictionary with concentration metrics
    """
    top_3_revenue = df.head(3)['Revenue'].sum()
    top_10_revenue = df.head(10)['Revenue'].sum()

    # Avoid division by zero
    if top_10_revenue > 0:
        top_3_share = (top_3_revenue / top_10_revenue) * 100
    else:
        top_3_share = 0.0

    return {
        'top_3_revenue': top_3_revenue,
        'top_10_revenue': top_10_revenue,
        'top_3_share_percentage': top_3_share
    }


def get_top_seller_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze the #1 seller in the category.

    Args:
        df: Cleaned DataFrame sorted by revenue

    Returns:
        Dictionary with top seller metrics
    """
    if len(df) == 0:
        return {
            'brand': 'N/A',
            'price': 0,
            'revenue': 0,
            'units': 0,
            'reviews': 0,
            'rating': 0
        }

    top_product = df.iloc[0]

    return {
        'brand': top_product.get('Brand', 'N/A'),
        'price': top_product.get('Price', 0),
        'revenue': top_product.get('Revenue', 0),
        'units': top_product.get('Sales', 0),
        'reviews': top_product.get('Review Count', 0),
        'rating': top_product.get('Ratings', 0)
    }


def calculate_rating_analysis(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate rating metrics for top products.

    Args:
        df: Cleaned DataFrame

    Returns:
        Dictionary with rating metrics
    """
    top_20 = df.head(20)
    avg_rating = top_20['Ratings'].mean()

    return {
        'average_rating_top_20': avg_rating,
        'min_rating': top_20['Ratings'].min(),
        'max_rating': top_20['Ratings'].max()
    }


def calculate_price_segments(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Analyze price segments in the market.

    Args:
        df: Cleaned DataFrame

    Returns:
        Dictionary with price segment analysis
    """
    # Define price ranges (in ₹)
    budget_max = 400
    mid_range_max = 800

    # Filter by price segments (use .loc to avoid ambiguous Series comparison)
    budget = df.loc[df['Price'] < budget_max].copy()
    mid_range = df.loc[(df['Price'] >= budget_max) & (df['Price'] < mid_range_max)].copy()
    premium = df.loc[df['Price'] >= mid_range_max].copy()

    return {
        'budget': {
            'range': f'<₹{budget_max}',
            'count': len(budget),
            'revenue': budget['Revenue'].sum(),
            'avg_price': budget['Price'].mean() if len(budget) > 0 else 0
        },
        'mid_range': {
            'range': f'₹{budget_max}-{mid_range_max}',
            'count': len(mid_range),
            'revenue': mid_range['Revenue'].sum(),
            'avg_price': mid_range['Price'].mean() if len(mid_range) > 0 else 0
        },
        'premium': {
            'range': f'>₹{mid_range_max}',
            'count': len(premium),
            'revenue': premium['Revenue'].sum(),
            'avg_price': premium['Price'].mean() if len(premium) > 0 else 0
        }
    }


def calculate_all_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate all metrics for a product category.

    Args:
        df: Cleaned DataFrame

    Returns:
        Dictionary with all metrics
    """
    if df is None or len(df) == 0:
        return None

    metrics = {
        'market_size': calculate_market_size(df),
        'market_concentration': calculate_market_concentration(df),
        'top_seller': get_top_seller_analysis(df),
        'rating_analysis': calculate_rating_analysis(df),
        'price_segments': calculate_price_segments(df),
        'total_products': len(df),
        'median_price': df['Price'].median()
    }

    return metrics


def format_currency(value: float) -> str:
    """
    Format value as Indian currency.

    Args:
        value: Numeric value

    Returns:
        Formatted string with ₹ symbol and lakhs notation
    """
    # Convert pandas Series/arrays to scalar
    if hasattr(value, '__len__') and not isinstance(value, str):
        # It's an array-like object (Series, ndarray, etc.)
        if len(value) == 1:
            value = float(value.iloc[0]) if hasattr(value, 'iloc') else float(value[0])
        else:
            # Multiple values - shouldn't happen, but handle gracefully
            value = float(value.iloc[0]) if hasattr(value, 'iloc') else float(value[0])
    else:
        value = float(value)

    if value >= 100000:  # 1 lakh
        return f"₹{value/100000:.2f}L"
    elif value >= 1000:  # 1 thousand
        return f"₹{value/1000:.1f}K"
    else:
        return f"₹{value:.0f}"


def format_number(value: float) -> str:
    """
    Format large numbers with K/L notation.

    Args:
        value: Numeric value

    Returns:
        Formatted string
    """
    # Convert pandas Series/arrays to scalar
    if hasattr(value, '__len__') and not isinstance(value, str):
        # It's an array-like object (Series, ndarray, etc.)
        if len(value) == 1:
            value = float(value.iloc[0]) if hasattr(value, 'iloc') else float(value[0])
        else:
            # Multiple values - shouldn't happen, but handle gracefully
            value = float(value.iloc[0]) if hasattr(value, 'iloc') else float(value[0])
    else:
        value = float(value)

    if value >= 100000:  # 1 lakh
        return f"{value/100000:.2f}L"
    elif value >= 1000:  # 1 thousand
        return f"{value/1000:.1f}K"
    else:
        return f"{value:.0f}"
