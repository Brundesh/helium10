"""
Flag generation system for Amazon FBA opportunity analysis.
Generates RED/YELLOW/GREEN flags based on metrics and provides recommendations.
"""

from typing import Dict, Any, List, Optional


def generate_flags(xray_metrics: Dict[str, Any],
                   magnet_metrics: Dict[str, Any] = None,
                   demand_supply: Dict[str, Any] = None,
                   scores: Dict[str, Any] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate RED/YELLOW/GREEN flags based on metrics.

    Args:
        xray_metrics: X-Ray metrics dictionary
        magnet_metrics: Optional Magnet demand metrics
        demand_supply: Optional demand/supply ratio analysis
        scores: Optional viability scores

    Returns:
        Dictionary with red_flags, yellow_flags, and green_signals lists
    """
    red_flags = []
    yellow_flags = []
    green_signals = []

    # === X-RAY BASED FLAGS ===

    # Market size flags
    market_size = xray_metrics['market_size']['estimated_total_market']
    if market_size < 300000:  # <3L
        red_flags.append({
            'message': f'Very small market size ({format_currency_short(market_size)})',
            'metric': 'market_size',
            'value': market_size
        })
    elif market_size < 500000:  # 3-5L
        yellow_flags.append({
            'message': f'Small market size ({format_currency_short(market_size)})',
            'metric': 'market_size',
            'value': market_size
        })
    elif market_size > 2000000:  # >20L
        green_signals.append({
            'message': f'Large market size ({format_currency_short(market_size)})',
            'metric': 'market_size',
            'value': market_size
        })

    # Market concentration flags
    top_3_share = xray_metrics['market_concentration']['top_3_share_percentage']
    if top_3_share > 75:
        red_flags.append({
            'message': f'Highly concentrated market (Top 3 control {top_3_share:.1f}%)',
            'metric': 'market_concentration',
            'value': top_3_share
        })
    elif top_3_share > 65:
        yellow_flags.append({
            'message': f'Concentrated market (Top 3 control {top_3_share:.1f}%)',
            'metric': 'market_concentration',
            'value': top_3_share
        })
    elif top_3_share < 40:
        green_signals.append({
            'message': f'Fragmented market - easier entry (Top 3 only {top_3_share:.1f}%)',
            'metric': 'market_concentration',
            'value': top_3_share
        })

    # Top seller competition flags
    top_seller_reviews = xray_metrics['top_seller']['reviews']
    if top_seller_reviews > 5000:
        red_flags.append({
            'message': f'Dominant top seller with {format_number_short(top_seller_reviews)} reviews',
            'metric': 'top_seller_reviews',
            'value': top_seller_reviews
        })
    elif top_seller_reviews > 3000:
        yellow_flags.append({
            'message': f'Strong top seller with {format_number_short(top_seller_reviews)} reviews',
            'metric': 'top_seller_reviews',
            'value': top_seller_reviews
        })
    elif top_seller_reviews < 1000:
        green_signals.append({
            'message': f'Weak top seller (only {format_number_short(top_seller_reviews)} reviews)',
            'metric': 'top_seller_reviews',
            'value': top_seller_reviews
        })

    # Price point flags
    median_price = xray_metrics['median_price']
    if median_price < 250:
        red_flags.append({
            'message': f'Low price point (₹{median_price:.0f}) - thin margins',
            'metric': 'median_price',
            'value': median_price
        })
    elif median_price < 350:
        yellow_flags.append({
            'message': f'Moderate price point (₹{median_price:.0f})',
            'metric': 'median_price',
            'value': median_price
        })
    elif median_price >= 500 and median_price <= 1500:
        green_signals.append({
            'message': f'Good price point (₹{median_price:.0f}) - healthy margins',
            'metric': 'median_price',
            'value': median_price
        })

    # Rating opportunity flags
    avg_rating = xray_metrics['rating_analysis']['average_rating_top_20']
    if avg_rating >= 3.8 and avg_rating <= 4.2:
        green_signals.append({
            'message': f'Quality gap opportunity (avg rating {avg_rating:.2f})',
            'metric': 'average_rating',
            'value': avg_rating
        })
    elif avg_rating < 3.5:
        yellow_flags.append({
            'message': f'Category quality issues (avg rating {avg_rating:.2f})',
            'metric': 'average_rating',
            'value': avg_rating
        })

    # === MAGNET BASED FLAGS ===

    if magnet_metrics is not None:
        search_volume = magnet_metrics['search_volume']
        trend = magnet_metrics['trend']

        # Search volume flags
        if search_volume < 2000:
            red_flags.append({
                'message': f'Very low search volume ({search_volume:,}/month)',
                'metric': 'search_volume',
                'value': search_volume
            })
        elif search_volume < 5000:
            yellow_flags.append({
                'message': f'Low search volume ({search_volume:,}/month)',
                'metric': 'search_volume',
                'value': search_volume
            })
        elif search_volume > 50000:
            green_signals.append({
                'message': f'High search volume ({search_volume:,}/month)',
                'metric': 'search_volume',
                'value': search_volume
            })

        # Trend flags
        if trend < -15:
            red_flags.append({
                'message': f'Market collapsing ({trend:+.0f}% trend)',
                'metric': 'trend',
                'value': trend
            })
        elif trend < -5:
            yellow_flags.append({
                'message': f'Declining market ({trend:+.0f}% trend)',
                'metric': 'trend',
                'value': trend
            })
        elif trend > 10:
            green_signals.append({
                'message': f'Growing market ({trend:+.0f}% trend)',
                'metric': 'trend',
                'value': trend
            })

    # === DEMAND/SUPPLY RATIO FLAGS ===

    if demand_supply is not None:
        ratio = demand_supply['ratio']

        if ratio < 1.0:
            red_flags.append({
                'message': f'Oversupplied market (ratio: {ratio:.1f})',
                'metric': 'demand_supply_ratio',
                'value': ratio
            })
        elif ratio < 2.0:
            yellow_flags.append({
                'message': f'Low demand/supply ratio ({ratio:.1f})',
                'metric': 'demand_supply_ratio',
                'value': ratio
            })
        elif ratio > 4.0:
            green_signals.append({
                'message': f'Excellent demand/supply ratio ({ratio:.1f})',
                'metric': 'demand_supply_ratio',
                'value': ratio
            })

        # GOLDMINE COMBO: High volume + good ratio
        if magnet_metrics is not None:
            search_volume = magnet_metrics['search_volume']
            if search_volume > 50000 and ratio > 3.0:
                green_signals.append({
                    'message': f'GOLDMINE: High demand ({search_volume:,}) + good ratio ({ratio:.1f})',
                    'metric': 'goldmine_combo',
                    'value': {'volume': search_volume, 'ratio': ratio}
                })

    return {
        'red_flags': red_flags,
        'yellow_flags': yellow_flags,
        'green_signals': green_signals
    }


def get_recommendation(scores: Dict[str, Any], flags: Dict[str, List[Dict[str, Any]]],
                      demand_supply: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate final recommendation based on scores and flags.

    Args:
        scores: Viability scores dictionary
        flags: Flags dictionary from generate_flags
        demand_supply: Optional demand/supply ratio analysis

    Returns:
        Dictionary with action, emoji, reasoning, and risk_level
    """
    score_percentage = scores.get('score_percentage', 0)
    red_count = len(flags['red_flags'])
    yellow_count = len(flags['yellow_flags'])
    green_count = len(flags['green_signals'])

    # Determine action based on score + flags
    if score_percentage >= 85 and red_count == 0:
        action = 'STRONG_GO'
        emoji = '🔥'
        risk_level = 'LOW'
        reasoning = (
            f"This is an excellent opportunity with a {score_percentage:.0f}% score and no red flags. "
            f"The market shows strong fundamentals "
        )
    elif score_percentage >= 70 and red_count <= 1:
        action = 'PROCEED'
        emoji = '✅'
        risk_level = 'MEDIUM'
        reasoning = (
            f"This is a good opportunity with a {score_percentage:.0f}% score. "
        )
    elif score_percentage >= 60 or red_count == 2:
        action = 'RISKY'
        emoji = '⚠️'
        risk_level = 'HIGH'
        reasoning = (
            f"This opportunity is risky with a {score_percentage:.0f}% score and {red_count} red flag(s). "
        )
    else:  # score < 60 or >= 3 red flags
        action = 'SKIP'
        emoji = '❌'
        risk_level = 'VERY HIGH'
        reasoning = (
            f"This opportunity should be skipped with a {score_percentage:.0f}% score and {red_count} red flag(s). "
        )

    # Add context about flags
    if green_count > 0:
        reasoning += f"Found {green_count} positive signal(s). "
    if yellow_count > 0:
        reasoning += f"Note {yellow_count} caution area(s). "
    if red_count > 0:
        reasoning += f"Critical: {red_count} deal-breaker(s) identified."

    # Add demand/supply context if available
    if demand_supply is not None:
        verdict = demand_supply['verdict']
        ratio = demand_supply['ratio']
        if verdict in ['EXCELLENT', 'GOOD']:
            reasoning += f" Strong demand/supply ratio ({ratio:.1f})."
        elif verdict == 'AVOID':
            reasoning += f" Poor demand/supply ratio ({ratio:.1f})."

    return {
        'action': action,
        'emoji': emoji,
        'reasoning': reasoning.strip(),
        'risk_level': risk_level,
        'red_count': red_count,
        'yellow_count': yellow_count,
        'green_count': green_count
    }


def format_currency_short(value: float) -> str:
    """Format currency for flag messages."""
    if value >= 100000:
        return f"₹{value/100000:.1f}L"
    elif value >= 1000:
        return f"₹{value/1000:.0f}K"
    else:
        return f"₹{value:.0f}"


def format_number_short(value: float) -> str:
    """Format numbers for flag messages."""
    if value >= 100000:
        return f"{value/100000:.1f}L"
    elif value >= 1000:
        return f"{value/1000:.1f}K"
    else:
        return f"{value:.0f}"


def get_flag_summary_text(flags: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Generate human-readable summary of flags.

    Args:
        flags: Flags dictionary

    Returns:
        Formatted text summary
    """
    red_flags = flags['red_flags']
    yellow_flags = flags['yellow_flags']
    green_signals = flags['green_signals']

    summary = "FLAGS & SIGNALS SUMMARY\n" + "=" * 40 + "\n\n"

    # Red flags
    if red_flags:
        summary += f"🚨 RED FLAGS ({len(red_flags)}):\n"
        for flag in red_flags:
            summary += f"  ❌ {flag['message']}\n"
        summary += "\n"
    else:
        summary += "🚨 RED FLAGS (0): None\n\n"

    # Yellow flags
    if yellow_flags:
        summary += f"⚠️  YELLOW FLAGS ({len(yellow_flags)}):\n"
        for flag in yellow_flags:
            summary += f"  ⚠️  {flag['message']}\n"
        summary += "\n"
    else:
        summary += "⚠️  YELLOW FLAGS (0): None\n\n"

    # Green signals
    if green_signals:
        summary += f"✅ GREEN SIGNALS ({len(green_signals)}):\n"
        for flag in green_signals:
            summary += f"  ✅ {flag['message']}\n"
    else:
        summary += "✅ GREEN SIGNALS (0): None\n"

    return summary
