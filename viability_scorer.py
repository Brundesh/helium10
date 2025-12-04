"""
Viability scoring system for Amazon FBA product opportunities.
Scores products based on market size, fragmentation, competition, ratings, and price.
"""

from typing import Dict, Any, Tuple


def score_market_size(estimated_total_market: float) -> Tuple[int, str]:
    """
    Score based on market size (0-20 points).

    Args:
        estimated_total_market: Estimated total market revenue

    Returns:
        Tuple of (score, explanation)
    """
    if estimated_total_market > 2000000:  # >20L
        return 20, "Excellent market size (>₹20L)"
    elif estimated_total_market >= 1000000:  # 10-20L
        return 15, "Good market size (₹10-20L)"
    elif estimated_total_market >= 500000:  # 5-10L
        return 10, "Moderate market size (₹5-10L)"
    else:  # <5L
        return 5, "Small market size (<₹5L)"


def score_market_fragmentation(top_3_share: float) -> Tuple[int, str]:
    """
    Score based on market fragmentation (0-20 points).
    Lower concentration = higher fragmentation = better opportunity.

    Args:
        top_3_share: Percentage of revenue held by top 3 sellers

    Returns:
        Tuple of (score, explanation)
    """
    if top_3_share < 30:
        return 20, "Highly fragmented market (Top 3 <30%)"
    elif top_3_share < 50:
        return 15, "Moderately fragmented (Top 3 30-50%)"
    elif top_3_share < 70:
        return 10, "Somewhat concentrated (Top 3 50-70%)"
    else:
        return 5, "Highly concentrated market (Top 3 >70%)"


def score_top_seller_reviews(review_count: float) -> Tuple[int, str]:
    """
    Score based on top seller's review count (0-15 points).
    Fewer reviews = easier to compete = better opportunity.

    Args:
        review_count: Number of reviews for top seller

    Returns:
        Tuple of (score, explanation)
    """
    if review_count < 500:
        return 15, "Low competition (Top seller <500 reviews)"
    elif review_count < 1000:
        return 12, "Moderate competition (500-1K reviews)"
    elif review_count < 3000:
        return 8, "High competition (1K-3K reviews)"
    else:
        return 3, "Very high competition (>3K reviews)"


def score_average_rating(avg_rating: float) -> Tuple[int, str]:
    """
    Score based on average rating of top 20 products (0-15 points).
    Mid-range ratings indicate opportunity for improvement.

    Args:
        avg_rating: Average rating of top 20 products

    Returns:
        Tuple of (score, explanation)
    """
    if 3.8 <= avg_rating < 4.1:
        return 15, "Great opportunity (3.8-4.1 rating - room for improvement)"
    elif 4.1 <= avg_rating < 4.3:
        return 10, "Good opportunity (4.1-4.3 rating)"
    elif avg_rating >= 4.3:
        return 5, "Satisfied customers (>4.3 rating - less opportunity)"
    else:  # <3.8
        return 10, "Category issues (<3.8 rating - risky)"


def score_price_viability(median_price: float) -> Tuple[int, str]:
    """
    Score based on median price (0-10 points).
    Higher prices = better margins = better opportunity.

    Args:
        median_price: Median price in the category

    Returns:
        Tuple of (score, explanation)
    """
    if median_price > 500:
        return 10, "Good margins (Median >₹500)"
    elif median_price >= 300:
        return 7, "Moderate margins (Median ₹300-500)"
    else:
        return 4, "Low margins (Median <₹300)"


def calculate_viability_score(metrics: Dict[str, Any], magnet_metrics: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Calculate overall viability score.

    WITHOUT Magnet data: 0-100 points
    WITH Magnet data: 0-150 points (includes demand/supply analysis)

    Args:
        metrics: Dictionary containing X-Ray metrics
        magnet_metrics: Optional dictionary from magnet_processor.calculate_demand_supply_ratio

    Returns:
        Dictionary with score breakdown and total
    """
    if metrics is None:
        return {
            'total_score': 0,
            'max_score': 100,
            'score_percentage': 0.0,
            'breakdown': {},
            'grade': 'F',
            'recommendation': 'Invalid data'
        }

    # Extract X-Ray values
    market_size = metrics['market_size']['estimated_total_market']
    top_3_share = metrics['market_concentration']['top_3_share_percentage']
    top_seller_reviews = metrics['top_seller']['reviews']
    avg_rating = metrics['rating_analysis']['average_rating_top_20']
    median_price = metrics['median_price']

    # Calculate X-Ray scores (base 100 points)
    size_score, size_reason = score_market_size(market_size)
    frag_score, frag_reason = score_market_fragmentation(top_3_share)
    review_score, review_reason = score_top_seller_reviews(top_seller_reviews)
    rating_score, rating_reason = score_average_rating(avg_rating)
    price_score, price_reason = score_price_viability(median_price)

    # Base total (X-Ray only)
    total_score = size_score + frag_score + review_score + rating_score + price_score

    # Build breakdown dictionary
    breakdown = {
        'market_size': {
            'score': size_score,
            'max': 20,
            'reason': size_reason
        },
        'market_fragmentation': {
            'score': frag_score,
            'max': 20,
            'reason': frag_reason
        },
        'competition': {
            'score': review_score,
            'max': 15,
            'reason': review_reason
        },
        'customer_satisfaction': {
            'score': rating_score,
            'max': 15,
            'reason': rating_reason
        },
        'price_viability': {
            'score': price_score,
            'max': 10,
            'reason': price_reason
        }
    }

    # Add Magnet scores if available (adds 50 points: 25 demand + 25 supply)
    max_score = 100
    if magnet_metrics is not None:
        max_score = 150
        demand_score = magnet_metrics['demand_score']
        supply_score = magnet_metrics['supply_score']
        total_score += demand_score + supply_score

        breakdown['demand'] = {
            'score': demand_score,
            'max': 25,
            'reason': f"{magnet_metrics['demand_tier']} demand ({magnet_metrics.get('search_volume', 0):,} searches/month)"
        }
        breakdown['supply_balance'] = {
            'score': supply_score,
            'max': 25,
            'reason': f"{magnet_metrics['supply_tier']} ({magnet_metrics.get('competing_products', 0):,} competitors)"
        }

    # Calculate percentage score
    score_percentage = (total_score / max_score) * 100

    # Determine grade and recommendation based on percentage
    if score_percentage >= 85:
        grade = 'A+'
        recommendation = '🔥 Excellent opportunity!'
        color = 'green'
    elif score_percentage >= 70:
        grade = 'A'
        recommendation = '✅ Good opportunity'
        color = 'lightgreen'
    elif score_percentage >= 60:
        grade = 'B'
        recommendation = '⚠️ Risky - proceed with caution'
        color = 'orange'
    else:
        grade = 'C'
        recommendation = '❌ Skip - poor opportunity'
        color = 'red'

    return {
        'total_score': total_score,
        'max_score': max_score,
        'score_percentage': score_percentage,
        'grade': grade,
        'recommendation': recommendation,
        'color': color,
        'breakdown': breakdown
    }


def get_score_color(score: float) -> str:
    """
    Get color code for score visualization.

    Args:
        score: Viability score (0-100)

    Returns:
        Color name for styling
    """
    if score >= 85:
        return 'green'
    elif score >= 70:
        return 'lightgreen'
    elif score >= 60:
        return 'orange'
    else:
        return 'red'


def get_score_emoji(score: float, rank: int = None) -> str:
    """
    Get emoji indicator for score.

    Args:
        score: Viability score (0-100)
        rank: Product rank (1 = best)

    Returns:
        Emoji string
    """
    if rank == 1:
        return '🔥'
    elif score >= 85:
        return '✅'
    elif score >= 60:
        return '⚠️'
    else:
        return '❌'
