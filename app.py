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


def process_uploaded_files(uploaded_files) -> Dict[str, Any]:
    """
    Process all uploaded CSV files.

    Args:
        uploaded_files: List of uploaded file objects

    Returns:
        Dictionary mapping product names to their data and metrics
    """
    products_data = {}

    for uploaded_file in uploaded_files:
        try:
            # Extract product name from filename (remove .csv extension)
            product_name = uploaded_file.name.replace('.csv', '')

            # Load and clean data
            df = load_and_clean_csv(uploaded_file)

            if not validate_dataframe(df):
                st.error(f"❌ Invalid data structure in {uploaded_file.name}")
                continue

            # Calculate metrics
            metrics = calculate_all_metrics(df)

            # Calculate viability score
            viability = calculate_viability_score(metrics)

            # Store everything
            products_data[product_name] = {
                'dataframe': df,
                'metrics': metrics,
                'viability': viability
            }

            st.success(f"✅ Loaded: {product_name} ({len(df)} products)")

        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")

    return products_data


def create_comparison_dataframe(products_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Create comparison DataFrame for all products.

    Args:
        products_data: Dictionary of product data

    Returns:
        DataFrame with comparison metrics
    """
    comparison_rows = []

    for product_name, data in products_data.items():
        metrics = data['metrics']
        viability = data['viability']

        row = {
            'Product': product_name,
            'Market Size': metrics['market_size']['estimated_total_market'],
            'Top 3 Share %': metrics['market_concentration']['top_3_share_percentage'],
            'Top Seller Reviews': metrics['top_seller']['reviews'],
            'Avg Rating': metrics['rating_analysis']['average_rating_top_20'],
            'Median Price': metrics['median_price'],
            'Viability Score': viability['total_score'],
            'Grade': viability['grade'],
            'Recommendation': viability['recommendation']
        }
        comparison_rows.append(row)

    # Create DataFrame and sort by viability score
    df = pd.DataFrame(comparison_rows)
    df = df.sort_values('Viability Score', ascending=False).reset_index(drop=True)
    df['Rank'] = range(1, len(df) + 1)

    # Reorder columns
    df = df[['Rank', 'Product', 'Market Size', 'Top 3 Share %', 'Top Seller Reviews',
             'Avg Rating', 'Median Price', 'Viability Score', 'Grade', 'Recommendation']]

    return df


def display_comparison_table(comparison_df: pd.DataFrame):
    """
    Display formatted comparison table.

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

    # Add emoji based on rank
    display_df['Emoji'] = display_df.apply(
        lambda row: get_score_emoji(row['Viability Score'], row['Rank']),
        axis=1
    )

    # Reorder to show emoji first
    display_df = display_df[['Emoji', 'Rank', 'Product', 'Market Size', 'Top 3 Share %',
                             'Top Seller Reviews', 'Avg Rating', 'Median Price',
                             'Viability Score', 'Grade', 'Recommendation']]

    # Display table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Emoji": st.column_config.TextColumn("", width="small"),
            "Viability Score": st.column_config.ProgressColumn(
                "Score",
                format="%d",
                min_value=0,
                max_value=100,
            ),
        }
    )

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Products Analyzed", len(comparison_df))
    with col2:
        excellent = len(comparison_df.loc[comparison_df['Viability Score'] >= 85])
        st.metric("Excellent Opportunities", excellent)
    with col3:
        good = len(comparison_df.loc[comparison_df['Viability Score'] >= 70])
        st.metric("Good+ Opportunities", good)
    with col4:
        avg_score = comparison_df['Viability Score'].mean()
        st.metric("Average Score", f"{avg_score:.1f}")


def display_detailed_view(product_name: str, product_data: Dict[str, Any]):
    """
    Display detailed analysis for a single product.

    Args:
        product_name: Name of the product
        product_data: Data dictionary for the product
    """
    df = product_data['dataframe']
    metrics = product_data['metrics']
    viability = product_data['viability']

    st.header(f"🔍 Detailed Analysis: {product_name}")

    # Viability Score Card
    col1, col2 = st.columns([1, 2])

    with col1:
        score = viability['total_score']
        grade = viability['grade']
        recommendation = viability['recommendation']

        # Determine color class
        if score >= 85:
            score_class = "score-excellent"
        elif score >= 70:
            score_class = "score-good"
        elif score >= 60:
            score_class = "score-risky"
        else:
            score_class = "score-poor"

        st.markdown(f'<div class="big-score {score_class}">{score}</div>', unsafe_allow_html=True)
        st.markdown(f"### Grade: {grade}")
        st.markdown(f"### {recommendation}")

    with col2:
        st.subheader("Score Breakdown")
        breakdown = viability['breakdown']

        for category, details in breakdown.items():
            score_pct = (details['score'] / details['max']) * 100
            st.write(f"**{category.replace('_', ' ').title()}**: {details['score']}/{details['max']}")
            st.progress(score_pct / 100)
            st.caption(details['reason'])

    st.divider()

    # Market Metrics
    st.subheader("📈 Market Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Estimated Total Market",
            format_currency(metrics['market_size']['estimated_total_market'])
        )
    with col2:
        st.metric(
            "Top 10 Revenue",
            format_currency(metrics['market_size']['top_10_revenue'])
        )
    with col3:
        st.metric(
            "Top 3 Market Share",
            f"{metrics['market_concentration']['top_3_share_percentage']:.1f}%"
        )
    with col4:
        st.metric(
            "Median Price",
            format_currency(metrics['median_price'])
        )

    st.divider()

    # Top Seller Analysis
    st.subheader("🏆 Top Seller Analysis")
    top_seller = metrics['top_seller']

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
    price_segments = metrics['price_segments']

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
        st.header("📁 Upload CSV Files")
        st.markdown("Upload one or more Helium 10 Xray CSV exports")

        uploaded_files = st.file_uploader(
            "Choose CSV files",
            type=['csv'],
            accept_multiple_files=True,
            help="Upload Helium 10 Xray CSV exports for different product categories"
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

            if st.button("🔄 Process Files", type="primary"):
                with st.spinner("Processing CSV files..."):
                    st.session_state.products_data = process_uploaded_files(uploaded_files)

                if st.session_state.products_data:
                    st.session_state.comparison_df = create_comparison_dataframe(
                        st.session_state.products_data
                    )
                    st.success(f"✅ Processed {len(st.session_state.products_data)} products!")

        st.divider()

        # Instructions
        st.markdown("""
        ### 📝 Instructions
        1. Upload one or more CSV files
        2. Click "Process Files"
        3. View comparison table
        4. Select product for details
        5. Export results

        ### 📊 Required CSV Columns
        - ASIN
        - Brand
        - Price (₹)
        - Revenue
        - Sales
        - Review Count
        - Ratings
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
        col1, col2 = st.columns(2)

        with col1:
            csv_data = export_comparison_to_csv(st.session_state.comparison_df)
            st.download_button(
                label="📥 Download Comparison CSV",
                data=csv_data,
                file_name="product_comparison.csv",
                mime="text/csv",
                help="Download the comparison table as CSV"
            )

        with col2:
            if st.button("🗑️ Clear All Data"):
                st.session_state.clear()
                st.rerun()


if __name__ == "__main__":
    main()
