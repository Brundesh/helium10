# Amazon FBA Product Opportunity Analyzer

A Streamlit web application for analyzing Helium 10 Xray CSV exports to identify the best Amazon FBA product opportunities.

## Features

- **Multi-file Upload**: Upload and analyze multiple product categories at once
- **Comprehensive Metrics**: Calculates market size, concentration, competition, ratings, and pricing
- **Viability Scoring**: 0-100 point scoring system to rank opportunities
- **Visual Analytics**: Interactive charts and tables for easy comparison
- **Export Results**: Download comparison data as CSV
- **Smart Data Cleaning**: Handles messy CSV data with automatic cleaning

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup Steps

1. Clone or download this repository:
```bash
cd helium10
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser to the URL shown (typically `http://localhost:8501`)

## Usage

### Step 1: Prepare Your Data

Export product data from Helium 10 Xray as CSV files. Each CSV should contain competitor data for one product category.

**Required CSV Columns:**
- `ASIN` - Amazon product identifier
- `Brand` - Brand name
- `Price` or `Price  ₹` - Product price
- `Revenue` - Monthly revenue estimate
- `Sales` - Monthly units sold
- `Review Count` - Number of customer reviews
- `Ratings` - Star rating (1-5)
- `Product Details` (optional) - Product title/description

### Step 2: Upload Files

1. Click "Browse files" or drag & drop CSV files into the upload area
2. Upload one or more CSV files (one per product category)
3. Click "Process Files" to analyze

### Step 3: Review Results

**Comparison Table** shows all products ranked by viability score:
- Market size and concentration metrics
- Competition indicators
- Pricing analysis
- Overall viability score (0-100)

**Detailed View** for each product includes:
- Score breakdown by category
- Top 10 products analysis
- Price segment distribution
- Revenue charts

### Step 4: Export Results

Click "Download Comparison CSV" to export the comparison table for further analysis.

## Understanding the Viability Score

The app calculates a 0-100 point viability score based on five criteria:

### 1. Market Size (20 points)
- **>₹20L**: 20 pts - Excellent market size
- **₹10-20L**: 15 pts - Good market size
- **₹5-10L**: 10 pts - Moderate market size
- **<₹5L**: 5 pts - Small market size

### 2. Market Fragmentation (20 points)
Measures how concentrated the market is among top sellers:
- **Top 3 <30%**: 20 pts - Highly fragmented (best)
- **Top 3 30-50%**: 15 pts - Moderately fragmented
- **Top 3 50-70%**: 10 pts - Somewhat concentrated
- **Top 3 >70%**: 5 pts - Highly concentrated (monopoly)

### 3. Competition Level (15 points)
Based on top seller's review count:
- **<500 reviews**: 15 pts - Easy to compete
- **500-1,000 reviews**: 12 pts - Moderate competition
- **1,000-3,000 reviews**: 8 pts - High competition
- **>3,000 reviews**: 3 pts - Very difficult to compete

### 4. Customer Satisfaction (15 points)
Average rating of top 20 products:
- **3.8-4.1**: 15 pts - Room for improvement (best opportunity)
- **4.1-4.3**: 10 pts - Good opportunity
- **>4.3**: 5 pts - Satisfied customers (harder to differentiate)
- **<3.8**: 10 pts - Category has issues (risky)

### 5. Price Viability (10 points)
Median price in category:
- **>₹500**: 10 pts - Good profit margins
- **₹300-500**: 7 pts - Moderate margins
- **<₹300**: 4 pts - Low margins

### Score Interpretation

- **85-100** 🔥 **Grade A+**: Excellent opportunity - highly recommended
- **70-84** ✅ **Grade A**: Good opportunity - worth pursuing
- **60-69** ⚠️ **Grade B**: Risky - proceed with caution
- **<60** ❌ **Grade C**: Poor opportunity - skip

## Project Structure

```
helium10/
├── app.py                    # Main Streamlit application
├── data_processor.py         # CSV parsing and data cleaning
├── metrics_calculator.py     # Market metrics calculations
├── viability_scorer.py       # Scoring system logic
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── SAMPLE_CSV_STRUCTURE.md   # CSV format documentation
```

## Metrics Explained

### Market Size Metrics

- **Top 10 Revenue**: Sum of monthly revenue for top 10 products
- **Top 20 Revenue**: Sum of monthly revenue for top 20 products
- **Estimated Total Market**: Top 20 revenue × 2 (assumes top 20 = ~50% of market)

### Market Concentration

- **Top 3 Share %**: (Top 3 revenue / Top 10 revenue) × 100
- Lower percentage = more fragmented = easier to enter

### Top Seller Analysis

Detailed metrics for the #1 revenue-generating product:
- Brand, price, revenue, units sold
- Review count (competition indicator)
- Star rating

### Price Segments

Products are categorized into three segments:
- **Budget**: <₹400
- **Mid-range**: ₹400-800
- **Premium**: >₹800

Each segment shows count, total revenue, and average price.

## Troubleshooting

### "Missing required columns" Error

Ensure your CSV has all required columns. Column names are case-insensitive and the app handles variations like "Price  ₹" or "Price".

### "Error processing CSV file"

Common issues:
- CSV file is corrupted or not properly formatted
- Price/Revenue columns contain non-numeric values
- File encoding issues (try saving as UTF-8)

### No Products Showing

- Check that CSV has valid data (not all zeros or N/A)
- Ensure revenue values are present
- Look for duplicate ASINs that may be filtered out

### Charts Not Displaying

- Ensure Plotly is installed: `pip install plotly`
- Try refreshing the browser
- Check browser console for JavaScript errors

## Tips for Best Results

1. **Use Recent Data**: Export fresh data from Helium 10 for accurate analysis
2. **Multiple Categories**: Upload 10-20 product categories to compare
3. **Clean Data**: Remove test/invalid rows from CSV before uploading
4. **Consider Context**: Score is a guide, not absolute truth - use your judgment
5. **Verify Top Products**: Check actual Amazon listings to confirm data accuracy

## Advanced Usage

### Custom Scoring Weights

To adjust scoring criteria, edit [viability_scorer.py](viability_scorer.py):

```python
def calculate_viability_score(metrics):
    # Modify point allocations here
    size_score = score_market_size(market_size)  # Currently 20 pts max
    frag_score = score_market_fragmentation(top_3_share)  # 20 pts
    # ... etc
```

### Custom Price Segments

To change price range definitions, edit [metrics_calculator.py](metrics_calculator.py):

```python
def calculate_price_segments(df):
    budget_max = 400  # Change this value
    mid_range_max = 800  # Change this value
    # ...
```

## Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualizations
- **openpyxl**: Excel file support (for future features)

## License

This project is provided as-is for personal and commercial use.

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Review the sample CSV structure
3. Verify your data format matches requirements

## Future Enhancements

Potential features for future versions:
- Historical trend analysis (multiple exports over time)
- Keyword opportunity analysis
- Competitor tracking
- Custom alert thresholds
- PDF report generation
- API integration with Helium 10

## Credits

Built for Amazon FBA sellers using Helium 10 Xray data exports.

---

**Happy Product Hunting! 🚀**
