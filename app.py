"""
Amazon FBA Product Opportunity Analyzer
Streamlit app for analyzing Helium 10 Xray CSV exports
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
import io

# Import custom modules
from data_processor import load_and_clean_csv, get_top_products, validate_dataframe
from metrics_calculator import (
    calculate_all_metrics,
    format_currency,
    format_number
)
from viability_scorer import calculate_viability_score, get_score_emoji
from magnet_processor import (
    parse_magnet_csv,
    calculate_demand_metrics,
    calculate_demand_supply_ratio,
    detect_trend_signal,
    validate_magnet_dataframe,
    extract_seed_keyword_from_filename
)
from flag_generator import generate_flags, get_recommendation, get_flag_summary_text
from excel_exporter import create_excel_export


# Page configuration
st.set_page_config(
    page_title="Amazon FBA Opportunity Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .score-excellent { color: #28a745; font-weight: bold; }
    .score-good { color: #90ee90; font-weight: bold; }
    .score-risky { color: #ffa500; font-weight: bold; }
    .score-poor { color: #dc3545; font-weight: bold; }
    .big-score {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)


def extract_subcategory_from_filename(filename: str) -> str:
    """
    Extract subcategory identifier from filename for matching X-Ray and Magnet files.

    Examples:
        "xray_laptop_stand.csv" → "laptop_stand"
        "IN_AMAZON_magnet__2025-12-04_yoga mat.csv" → "yoga_mat"
        "spice rack organizer.csv" → "spice_rack_organizer"

    Args:
        filename: CSV filename

    Returns:
        Standardized subcategory identifier
    """
    # Remove .csv extension
    name = filename.replace('.csv', '').lower()

    # Remove common prefixes
    for prefix in ['helium_10_xray_', 'xray_', 'magnet_', 'in_amazon_magnet__']:
        if name.startswith(prefix):
            name = name[len(prefix):]

    # Remove date patterns (e.g., "2025-12-04_")
    import re
    name = re.sub(r'\d{4}-\d{2}-\d{2}_?', '', name)

    # Replace spaces and special chars with underscore
    name = re.sub(r'[^a-z0-9]+', '_', name)

    # Remove leading/trailing underscores
    name = name.strip('_')

    return name


def match_xray_magnet_files(xray_files, magnet_files) -> List[Dict[str, Any]]:
    """
    Match X-Ray and Magnet files by subcategory name.

    Args:
        xray_files: List of X-Ray file objects
        magnet_files: List of Magnet file objects (can be None)

    Returns:
        List of dictionaries with subcategory, xray_file, magnet_file, and display_name
    """
    matched = []

    # Create mapping of subcategory to magnet file
    magnet_map = {}
    if magnet_files:
        for magnet_file in magnet_files:
            subcat = extract_subcategory_from_filename(magnet_file.name)
            magnet_map[subcat] = magnet_file

    # Match X-Ray files
    for xray_file in xray_files:
        subcat = extract_subcategory_from_filename(xray_file.name)

        # Try to find matching magnet file
        magnet_file = magnet_map.get(subcat, None)

        # Create display name (capitalize and replace underscores with spaces)
        display_name = subcat.replace('_', ' ').title()

        matched.append({
            'subcategory': subcat,
            'display_name': display_name,
            'xray_file': xray_file,
            'magnet_file': magnet_file
        })

    return matched


def process_uploaded_files(xray_files, magnet_files=None) -> Dict[str, Any]:
    """
    Process all uploaded CSV files (X-Ray required, Magnet optional).

    Args:
        xray_files: List of X-Ray uploaded file objects
        magnet_files: Optional list of Magnet uploaded file objects

    Returns:
        Dictionary mapping product names to their data and metrics
    """
    products_data = {}

    # Match files
    matched_files = match_xray_magnet_files(xray_files, magnet_files)

    for match in matched_files:
        subcategory = match['subcategory']
        display_name = match['display_name']
        xray_file = match['xray_file']
        magnet_file = match['magnet_file']

        try:
            # === Process X-Ray data ===
            df = load_and_clean_csv(xray_file)

            # Validate X-Ray data
            is_valid, xray_warnings = validate_dataframe(df)
            if not is_valid:
                st.error(f"❌ Invalid X-Ray data: {xray_warnings[0] if xray_warnings else 'Unknown error'}")
                continue

            # Calculate X-Ray metrics
            xray_metrics = calculate_all_metrics(df)

            # === Process Magnet data (if available) ===
            magnet_demand_metrics = None
            magnet_ds_ratio = None
            magnet_df = None
            magnet_warnings = []

            if magnet_file is not None:
                try:
                    magnet_df = parse_magnet_csv(magnet_file, magnet_file.name)
                    is_valid, warnings = validate_magnet_dataframe(magnet_df)

                    if is_valid:
                        magnet_demand_metrics = calculate_demand_metrics(
                            magnet_df,
                            filename=magnet_file.name,
                            seed_keyword=None
                        )
                        if magnet_demand_metrics:
                            magnet_ds_ratio = calculate_demand_supply_ratio(magnet_demand_metrics, xray_metrics)
                            # Add search_volume and competing_products to ds_ratio for scorer
                            magnet_ds_ratio['search_volume'] = magnet_demand_metrics['search_volume']
                            magnet_ds_ratio['competing_products'] = magnet_demand_metrics['competing_products']

                        magnet_warnings = warnings
                    else:
                        st.warning(f"⚠️ {magnet_file.name}: {warnings[0] if warnings else 'Invalid Magnet data'}")

                except Exception as e:
                    st.warning(f"⚠️ Error processing Magnet file {magnet_file.name}: {str(e)}")

            # === Calculate viability score (with or without Magnet) ===
            viability = calculate_viability_score(xray_metrics, magnet_ds_ratio)

            # === Generate flags and recommendation ===
            flags = generate_flags(
                xray_metrics,
                magnet_demand_metrics,
                magnet_ds_ratio,
                viability
            )
            recommendation = get_recommendation(viability, flags, magnet_ds_ratio)

            # === Store everything ===
            products_data[display_name] = {
                'subcategory': subcategory,
                'dataframe': df,
                'xray_metrics': xray_metrics,
                'magnet_df': magnet_df,
                'magnet_demand_metrics': magnet_demand_metrics,
                'magnet_ds_ratio': magnet_ds_ratio,
                'magnet_warnings': magnet_warnings,
                'viability': viability,
                'flags': flags,
                'recommendation': recommendation
            }

            # Success message
            if magnet_file:
                st.success(f"✅ {display_name}: Loaded X-Ray ({len(df)} products) + Magnet ({len(magnet_df)} keywords)")
            else:
                st.success(f"✅ {display_name}: Loaded X-Ray ({len(df)} products)")

            # Show X-Ray warnings
            for warning in xray_warnings:
                st.warning(f"⚠️ {display_name} (X-Ray): {warning}")

            # Show Magnet warnings
            for warning in magnet_warnings:
                st.warning(f"⚠️ {display_name} (Magnet): {warning}")

        except Exception as e:
            st.error(f"❌ Error processing {display_name}: {str(e)}")

    return products_data


def create_comparison_dataframe(products_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Create comparison DataFrame for all products (with optional Magnet data).

    Args:
        products_data: Dictionary of product data

    Returns:
        DataFrame with comparison metrics
    """
    comparison_rows = []
    has_magnet_data = False

    for product_name, data in products_data.items():
        xray_metrics = data['xray_metrics']
        viability = data['viability']
        magnet_demand = data.get('magnet_demand_metrics')
        magnet_ds = data.get('magnet_ds_ratio')
        recommendation = data.get('recommendation')
        flags = data.get('flags')

        row = {
            'Product': product_name,
            'Market Size': xray_metrics['market_size']['estimated_total_market'],
            'Top 3 Share %': xray_metrics['market_concentration']['top_3_share_percentage'],
            'Top Seller Reviews': xray_metrics['top_seller']['reviews'],
            'Avg Rating': xray_metrics['rating_analysis']['average_rating_top_20'],
            'Median Price': xray_metrics['median_price'],
        }

        # Add Magnet columns if available
        if magnet_demand is not None:
            has_magnet_data = True
            row['Search Volume'] = magnet_demand['search_volume']
            row['Trend %'] = magnet_demand['trend']
            row['D/S Ratio (Pg 1-2)'] = magnet_ds.get('ds_ratio', magnet_ds.get('ratio', 0)) if magnet_ds else 0
            row['Success Rate %'] = magnet_ds.get('success_rate', 0) if magnet_ds else 0
            row['Products Ranking'] = magnet_ds.get('xray_product_count', 0) if magnet_ds else 0
            row['Demand Score'] = magnet_ds['demand_score'] if magnet_ds else 0
            row['Supply Score'] = magnet_ds['supply_score'] if magnet_ds else 0
        else:
            row['Search Volume'] = None
            row['Trend %'] = None
            row['D/S Ratio (Pg 1-2)'] = None
            row['Success Rate %'] = None
            row['Products Ranking'] = None
            row['Demand Score'] = None
            row['Supply Score'] = None

        # Add score info
        row['Total Score'] = viability['total_score']
        row['Max Score'] = viability['max_score']
        row['Score %'] = viability['score_percentage']
        row['Grade'] = viability['grade']

        # Add flags count
        if flags:
            row['Red Flags'] = len(flags['red_flags'])
            row['Yellow Flags'] = len(flags['yellow_flags'])
            row['Green Signals'] = len(flags['green_signals'])
        else:
            row['Red Flags'] = 0
            row['Yellow Flags'] = 0
            row['Green Signals'] = 0

        # Add recommendation
        if recommendation:
            row['Action'] = recommendation['action']
            row['Risk Level'] = recommendation['risk_level']
        else:
            row['Action'] = viability['recommendation']
            row['Risk Level'] = 'UNKNOWN'

        comparison_rows.append(row)

    # Create DataFrame and sort by score percentage
    df = pd.DataFrame(comparison_rows)
    df = df.sort_values('Score %', ascending=False).reset_index(drop=True)
    df['Rank'] = range(1, len(df) + 1)

    # Reorder columns based on whether we have Magnet data
    base_cols = ['Rank', 'Product', 'Market Size', 'Top 3 Share %', 'Top Seller Reviews',
                 'Avg Rating', 'Median Price']

    if has_magnet_data:
        magnet_cols = ['Search Volume', 'Trend %', 'Products Ranking', 'D/S Ratio (Pg 1-2)',
                      'Success Rate %', 'Demand Score', 'Supply Score']
        # Remove None columns for products without Magnet data
        magnet_cols = [col for col in magnet_cols if df[col].notna().any()]
        cols = base_cols + magnet_cols
    else:
        cols = base_cols

    cols += ['Total Score', 'Max Score', 'Score %', 'Grade', 'Red Flags', 'Yellow Flags',
             'Green Signals', 'Action', 'Risk Level']

    df = df[cols]

    return df


def display_comparison_table(comparison_df: pd.DataFrame):
    """
    Display formatted comparison table (with optional Magnet columns).

    Args:
        comparison_df: Comparison DataFrame
    """
    st.header("📊 Product Comparison")

    # Format the DataFrame for display
    display_df = comparison_df.copy()

    # Format currency and numbers
    display_df['Market Size'] = display_df['Market Size'].apply(format_currency)
    display_df['Top 3 Share %'] = display_df['Top 3 Share %'].apply(lambda x: f"{x:.1f}%")
    display_df['Top Seller Reviews'] = display_df['Top Seller Reviews'].apply(format_number)
    display_df['Avg Rating'] = display_df['Avg Rating'].apply(lambda x: f"{x:.2f}⭐")
    display_df['Median Price'] = display_df['Median Price'].apply(format_currency)

    # Format Magnet columns if they exist
    if 'Search Volume' in display_df.columns and display_df['Search Volume'].notna().any():
        display_df['Search Volume'] = display_df['Search Volume'].apply(
            lambda x: f"{int(x):,}" if pd.notna(x) else "N/A"
        )
    if 'Trend %' in display_df.columns and display_df['Trend %'].notna().any():
        display_df['Trend %'] = display_df['Trend %'].apply(
            lambda x: f"{x:+.0f}%" if pd.notna(x) else "N/A"
        )
    if 'D/S Ratio (Pg 1-2)' in display_df.columns and display_df['D/S Ratio (Pg 1-2)'].notna().any():
        display_df['D/S Ratio (Pg 1-2)'] = display_df['D/S Ratio (Pg 1-2)'].apply(
            lambda x: f"{x:.0f}" if pd.notna(x) else "N/A"
        )
    if 'Success Rate %' in display_df.columns and display_df['Success Rate %'].notna().any():
        display_df['Success Rate %'] = display_df['Success Rate %'].apply(
            lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A"
        )

    # Add emoji for action
    def get_action_emoji(action):
        emoji_map = {
            'STRONG_GO': '🔥',
            'PROCEED': '✅',
            'RISKY': '⚠️',
            'SKIP': '❌'
        }
        return emoji_map.get(action, '❓')

    display_df['Emoji'] = display_df['Action'].apply(get_action_emoji)

    # Display table
    column_config = {
        "Emoji": st.column_config.TextColumn("", width="small"),
        "Score %": st.column_config.ProgressColumn(
            "Score %",
            format="%.1f%%",
            min_value=0,
            max_value=100,
        ),
    }

    # Add tooltips for Magnet columns if they exist
    if 'D/S Ratio (Pg 1-2)' in display_df.columns:
        column_config["D/S Ratio (Pg 1-2)"] = st.column_config.TextColumn(
            "D/S Ratio (Pg 1-2)",
            help="Searches per product ranking on pages 1-2. Higher = better opportunity for ranked products.",
            width="medium"
        )
    if 'Success Rate %' in display_df.columns:
        column_config["Success Rate %"] = st.column_config.TextColumn(
            "Success Rate %",
            help="% of total listings that rank on pages 1-2. Lower = harder to rank but bigger reward.",
            width="medium"
        )
    if 'Products Ranking' in display_df.columns:
        column_config["Products Ranking"] = st.column_config.NumberColumn(
            "Products Ranking",
            help="Number of products from X-Ray export ranking on pages 1-2",
            width="small"
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config=column_config
    )

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Analyzed", len(comparison_df))
    with col2:
        strong_go = len(comparison_df[comparison_df['Action'] == 'STRONG_GO'])
        st.metric("Strong Go", strong_go)
    with col3:
        proceed = len(comparison_df[comparison_df['Action'].isin(['STRONG_GO', 'PROCEED'])])
        st.metric("Go/Proceed", proceed)
    with col4:
        avg_score = comparison_df['Score %'].mean()
        st.metric("Avg Score %", f"{avg_score:.1f}%")


def display_detailed_view(product_name: str, product_data: Dict[str, Any]):
    """
    Display detailed analysis for a single product (with optional Magnet data).

    Args:
        product_name: Name of the product
        product_data: Data dictionary for the product
    """
    df = product_data['dataframe']
    xray_metrics = product_data['xray_metrics']
    viability = product_data['viability']
    magnet_demand = product_data.get('magnet_demand_metrics')
    magnet_ds = product_data.get('magnet_ds_ratio')
    flags = product_data.get('flags')
    recommendation_data = product_data.get('recommendation')

    st.header(f"🔍 Detailed Analysis: {product_name}")

    # === RECOMMENDATION BANNER ===
    if recommendation_data:
        action = recommendation_data['action']
        emoji = recommendation_data['emoji']
        reasoning = recommendation_data['reasoning']
        risk_level = recommendation_data['risk_level']

        # Color based on action
        if action == 'STRONG_GO':
            banner_color = '#28a745'
        elif action == 'PROCEED':
            banner_color = '#90ee90'
        elif action == 'RISKY':
            banner_color = '#ffa500'
        else:
            banner_color = '#dc3545'

        st.markdown(f"""
        <div style="background-color: {banner_color}; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0;">{emoji} {action.replace('_', ' ')}</h2>
            <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">{reasoning}</p>
            <p style="color: white; margin: 5px 0 0 0;"><strong>Risk Level: {risk_level}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    # === VIABILITY SCORE CARD ===
    col1, col2 = st.columns([1, 2])

    with col1:
        total_score = viability['total_score']
        max_score = viability['max_score']
        score_pct = viability['score_percentage']
        grade = viability['grade']

        # Determine color class
        if score_pct >= 85:
            score_class = "score-excellent"
        elif score_pct >= 70:
            score_class = "score-good"
        elif score_pct >= 60:
            score_class = "score-risky"
        else:
            score_class = "score-poor"

        st.markdown(f'<div class="big-score {score_class}">{total_score}/{max_score}</div>', unsafe_allow_html=True)
        st.markdown(f"### Grade: {grade} ({score_pct:.1f}%)")

    with col2:
        st.subheader("Score Breakdown")
        breakdown = viability['breakdown']

        for category, details in breakdown.items():
            score_pct_cat = (details['score'] / details['max']) * 100
            st.write(f"**{category.replace('_', ' ').title()}**: {details['score']}/{details['max']}")
            st.progress(score_pct_cat / 100)
            st.caption(details['reason'])

    st.divider()

    # === DEMAND ANALYSIS (if Magnet data available) ===
    if magnet_demand is not None and magnet_ds is not None:
        st.subheader("📊 DEMAND-SUPPLY ANALYSIS")

        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Primary Keyword", magnet_demand['seed_keyword'])

        with col2:
            search_vol = magnet_demand['search_volume']
            st.metric("Search Volume", f"{search_vol:,}/mo")

        with col3:
            trend = magnet_demand['trend']
            trend_signal = detect_trend_signal(trend)
            st.metric(
                "Trend",
                f"{trend:+.0f}% {trend_signal['emoji']}",
                delta=trend_signal['description']
            )

        with col4:
            xray_count = magnet_ds.get('xray_product_count', 0)
            st.metric("Products Ranking (Pg 1-2)", f"{xray_count}")

        # D/S Ratio card with new metrics
        st.markdown("### Demand Capture Analysis")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ds_ratio = magnet_ds.get('ds_ratio', magnet_ds.get('ratio', 0))
            verdict_emoji = magnet_ds['verdict_emoji']
            st.metric("D/S Ratio (Pg 1-2)", f"{ds_ratio:.0f} {verdict_emoji}")

        with col2:
            verdict = magnet_ds['verdict']
            st.metric("Verdict", verdict)

        with col3:
            success_rate = magnet_ds.get('success_rate', 0)
            st.metric("Success Rate", f"{success_rate:.2f}%")

        with col4:
            magnet_total = magnet_ds.get('magnet_total_listings', magnet_demand['competing_products'])
            st.metric("Total Market Listings", f"{magnet_total:,}")

        # Enhanced explanation box
        st.info(f"""
💡 **How to Read These Numbers:**

**D/S Ratio ({ds_ratio:.0f}):** Each product ranking on pages 1-2 captures ~{ds_ratio:.0f} searches/month on average.

**Success Rate ({success_rate:.2f}%):** Only {xray_count} of {magnet_total:,} total listings rank on first 2 pages.
This means {100 - success_rate:.1f}% of sellers failed to rank.

**Analysis:** {magnet_ds['reasoning']}
        """)

        # Top related keywords
        if magnet_demand['top_related_keywords']:
            st.markdown("### Top Related Keywords")
            related_data = []
            for kw in magnet_demand['top_related_keywords']:
                related_data.append({
                    'Keyword': kw['keyword'],
                    'Volume': f"{kw['volume']:,}",
                    'Trend': f"{kw['trend']:+.0f}%",
                    'Competitors': f"{kw['competitors']:,}"
                })

            st.dataframe(pd.DataFrame(related_data), use_container_width=True, hide_index=True)

        st.divider()

    # === FLAGS & SIGNALS ===
    if flags:
        st.subheader("🚨 FLAGS & SIGNALS")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"### ❌ Red Flags ({len(flags['red_flags'])})")
            if flags['red_flags']:
                for flag in flags['red_flags']:
                    st.error(f"❌ {flag['message']}")
            else:
                st.success("None")

        with col2:
            st.markdown(f"### ⚠️ Yellow Flags ({len(flags['yellow_flags'])})")
            if flags['yellow_flags']:
                for flag in flags['yellow_flags']:
                    st.warning(f"⚠️ {flag['message']}")
            else:
                st.info("None")

        with col3:
            st.markdown(f"### ✅ Green Signals ({len(flags['green_signals'])})")
            if flags['green_signals']:
                for flag in flags['green_signals']:
                    st.success(f"✅ {flag['message']}")
            else:
                st.info("None")

        st.divider()

    # === X-RAY MARKET METRICS (continue with existing code) ===

    # Market Metrics
    st.subheader("📈 Market Metrics (X-Ray)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Estimated Total Market",
            format_currency(xray_metrics['market_size']['estimated_total_market'])
        )
    with col2:
        st.metric(
            "Top 10 Revenue",
            format_currency(xray_metrics['market_size']['top_10_revenue'])
        )
    with col3:
        st.metric(
            "Top 3 Market Share",
            f"{xray_metrics['market_concentration']['top_3_share_percentage']:.1f}%"
        )
    with col4:
        st.metric(
            "Median Price",
            format_currency(xray_metrics['median_price'])
        )

    st.divider()

    # Top Seller Analysis
    st.subheader("🏆 Top Seller Analysis")
    top_seller = xray_metrics['top_seller']

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Brand", top_seller['brand'])
    with col2:
        st.metric("Price", format_currency(top_seller['price']))
    with col3:
        st.metric("Monthly Revenue", format_currency(top_seller['revenue']))
    with col4:
        st.metric("Monthly Units", format_number(top_seller['units']))
    with col5:
        st.metric("Reviews", format_number(top_seller['reviews']))

    st.divider()

    # Top 10 Products Table
    st.subheader("📋 Top 10 Products")
    top_10 = get_top_products(df, 10)
    display_top_10 = top_10[['Brand', 'Price', 'Revenue', 'Sales', 'Review Count', 'Ratings']].copy()
    display_top_10['Price'] = display_top_10['Price'].apply(format_currency)
    display_top_10['Revenue'] = display_top_10['Revenue'].apply(format_currency)
    display_top_10['Sales'] = display_top_10['Sales'].apply(format_number)
    display_top_10['Review Count'] = display_top_10['Review Count'].apply(format_number)
    display_top_10['Ratings'] = display_top_10['Ratings'].apply(lambda x: f"{x:.1f}⭐")

    st.dataframe(display_top_10, use_container_width=True, hide_index=True)

    st.divider()

    # Price Segments
    st.subheader("💰 Price Segment Analysis")
    price_segments = xray_metrics['price_segments']

    # Create chart data
    segment_data = []
    for segment_name, segment_info in price_segments.items():
        segment_data.append({
            'Segment': segment_name.replace('_', ' ').title(),
            'Range': segment_info['range'],
            'Revenue': segment_info['revenue'],
            'Count': segment_info['count']
        })

    segment_df = pd.DataFrame(segment_data)

    col1, col2 = st.columns(2)

    with col1:
        # Revenue by segment chart
        fig = px.bar(
            segment_df,
            x='Segment',
            y='Revenue',
            text='Revenue',
            title='Revenue by Price Segment',
            labels={'Revenue': 'Revenue (₹)'},
            color='Segment',
            color_discrete_map={
                'Budget': '#3498db',
                'Mid Range': '#2ecc71',
                'Premium': '#9b59b6'
            }
        )
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Product count by segment
        fig = px.pie(
            segment_df,
            values='Count',
            names='Segment',
            title='Product Count by Price Segment',
            color='Segment',
            color_discrete_map={
                'Budget': '#3498db',
                'Mid Range': '#2ecc71',
                'Premium': '#9b59b6'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    # Segment details table
    st.dataframe(
        segment_df.assign(Revenue=segment_df['Revenue'].apply(format_currency)),
        use_container_width=True,
        hide_index=True
    )


def export_comparison_to_csv(comparison_df: pd.DataFrame) -> bytes:
    """
    Export comparison DataFrame to CSV bytes.

    Args:
        comparison_df: Comparison DataFrame

    Returns:
        CSV data as bytes
    """
    output = io.BytesIO()
    comparison_df.to_csv(output, index=False)
    return output.getvalue()


def main():
    """Main application function."""

    # Title and description
    st.title("📊 Amazon FBA Product Opportunity Analyzer")
    st.markdown("### Analyze Helium 10 Xray CSV exports to find the best product opportunities")

    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Upload Analysis Data")

        # X-Ray files (required)
        st.subheader("📊 X-Ray Data (Required)")
        xray_files = st.file_uploader(
            "Upload X-Ray CSV files",
            type=['csv'],
            accept_multiple_files=True,
            key='xray',
            help="Export from Helium 10 X-Ray - one file per subcategory"
        )

        # Magnet files (optional)
        st.subheader("🔍 Magnet Data (Optional)")
        magnet_files = st.file_uploader(
            "Upload Magnet CSV files",
            type=['csv'],
            accept_multiple_files=True,
            key='magnet',
            help="Export from Helium 10 Magnet - matching subcategories for demand analysis"
        )

        st.info("💡 **Tip**: Name files consistently (e.g., `xray_laptop_stand.csv` + `magnet_laptop_stand.csv`) for automatic matching")

        # Process button
        if xray_files:
            st.success(f"✅ {len(xray_files)} X-Ray file(s)")
            if magnet_files:
                st.success(f"✅ {len(magnet_files)} Magnet file(s)")

            if st.button("🔄 Process Files", type="primary"):
                with st.spinner("Processing CSV files..."):
                    st.session_state.products_data = process_uploaded_files(xray_files, magnet_files)

                if st.session_state.products_data:
                    st.session_state.comparison_df = create_comparison_dataframe(
                        st.session_state.products_data
                    )
                    st.success(f"✅ Processed {len(st.session_state.products_data)} subcategories!")

        st.divider()

        # Instructions
        st.markdown("""
        ### 📝 Instructions
        1. Upload X-Ray CSV files (required)
        2. Upload Magnet CSV files (optional)
        3. Click "Process Files"
        4. View comparison table
        5. Select subcategory for details
        6. Export results

        ### 📊 Analysis Scoring
        **Without Magnet**: 0-100 points
        - Market Size, Fragmentation, Competition, Ratings, Price

        **With Magnet**: 0-150 points
        - Above 5 factors + Demand + Supply Balance
        """)

    # Main content area
    if 'products_data' not in st.session_state or not st.session_state.products_data:
        # Welcome screen
        st.info("👆 Upload CSV files using the sidebar to get started")

        st.markdown("""
        ## How It Works

        This tool analyzes Helium 10 Xray CSV exports to help you identify the best Amazon FBA product opportunities.

        ### Scoring Criteria (0-100 points)

        1. **Market Size (20 pts)**: Larger markets = more opportunity
        2. **Market Fragmentation (20 pts)**: Less concentrated = easier to enter
        3. **Competition Level (15 pts)**: Fewer reviews on top seller = easier to compete
        4. **Customer Satisfaction (15 pts)**: Mid-range ratings = room for improvement
        5. **Price Viability (10 pts)**: Higher prices = better margins

        ### Score Interpretation

        - **85-100** 🔥: Excellent opportunity - highly recommended
        - **70-84** ✅: Good opportunity - worth pursuing
        - **60-69** ⚠️: Risky - proceed with caution
        - **<60** ❌: Poor opportunity - skip

        """)

    else:
        # Display comparison table
        display_comparison_table(st.session_state.comparison_df)

        st.divider()

        # Product selector for detailed view
        st.subheader("🔍 Detailed Product Analysis")
        product_names = list(st.session_state.products_data.keys())

        # Sort by viability score
        product_names_sorted = st.session_state.comparison_df['Product'].tolist()

        selected_product = st.selectbox(
            "Select a product to view detailed analysis:",
            product_names_sorted,
            index=0
        )

        if selected_product:
            st.divider()
            display_detailed_view(
                selected_product,
                st.session_state.products_data[selected_product]
            )

        st.divider()

        # Export functionality
        st.subheader("💾 Export Results")
        col1, col2, col3 = st.columns(3)

        with col1:
            csv_data = export_comparison_to_csv(st.session_state.comparison_df)
            st.download_button(
                label="📥 CSV (Simple)",
                data=csv_data,
                file_name="product_comparison.csv",
                mime="text/csv",
                help="Download the comparison table as CSV"
            )

        with col2:
            with st.spinner("Generating Excel..."):
                excel_data = create_excel_export(
                    st.session_state.products_data,
                    st.session_state.comparison_df
                )
            st.download_button(
                label="📊 Excel (Full Report)",
                data=excel_data,
                file_name="helium10_analysis_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download comprehensive analysis with 4 sheets: Rankings, Detailed Metrics, Keyword Analysis, Action Plan"
            )

        with col3:
            if st.button("🗑️ Clear All Data"):
                st.session_state.clear()
                st.rerun()


if __name__ == "__main__":
    main()
