# Amazon FBA Product Opportunity Analyzer

A powerful Streamlit web application for analyzing Helium 10 data exports to identify the best Amazon FBA product opportunities. Combines **X-Ray competition data** with **Magnet keyword demand data** for complete supply-demand analysis.

## 🚀 New Features (Phase 1: Magnet Integration)

### Complete Demand-Supply Analysis
- **Dual Data Integration**: Combine X-Ray (competition) + Magnet (demand) for 360° market view
- **150-Point Scoring**: Enhanced scoring system (100 pts X-Ray + 50 pts demand/supply)
- **Automated Flags**: RED/YELLOW/GREEN signals for instant opportunity assessment
- **Smart File Matching**: Automatically pairs X-Ray and Magnet files by keyword
- **Comprehensive Excel Export**: 4-sheet workbook with rankings, metrics, keywords, and action plan

## Features

### Core Analysis
- **Multi-file Upload**: Analyze multiple product categories simultaneously
- **Comprehensive Metrics**: Market size, concentration, competition, ratings, pricing
- **Viability Scoring**: 0-150 point scoring system (0-100 without Magnet data)
- **Visual Analytics**: Interactive charts and comparison tables
- **Smart Data Cleaning**: Automatic handling of messy CSV exports

### Demand Analysis (with Magnet Data)
- **Search Volume Tracking**: Monthly keyword demand metrics
- **Trend Detection**: Identify growing, stable, or declining markets
- **D/S Ratio Calculation**: Searches per competitor (sweet spot finder)
- **Keyword Analysis**: Top 5 related keywords with metrics
- **Balance Scoring**: Demand score (25 pts) + Supply score (25 pts)

### Automated Insights
- **Flag System**:
  - 🚨 **RED FLAGS**: Deal-breakers (e.g., >5K reviews, <₹250 price, collapsing market)
  - ⚠️ **YELLOW FLAGS**: Caution areas (moderate risks)
  - ✅ **GREEN SIGNALS**: Opportunities (fragmentation, quality gaps, high demand)
- **Action Recommendations**: STRONG_GO / PROCEED / RISKY / SKIP with reasoning
- **Risk Assessment**: LOW / MEDIUM / HIGH / VERY HIGH risk levels

### Export Options
- **Simple CSV**: Quick comparison table export
- **Full Excel Report** (4 sheets):
  1. **Rankings**: All subcategories sorted by score
  2. **Detailed_Metrics**: Complete breakdown of every metric
  3. **Keyword_Analysis**: Top keywords per subcategory (Magnet data)
  4. **Action_Plan**: Only GO/PROCEED opportunities with priority ranking

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps

1. Navigate to project directory:
```bash
cd helium10
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open browser to `http://localhost:8501`

## Usage

### Step 1: Prepare Your Data

#### X-Ray Data (Required)
Export competition data from Helium 10 X-Ray as CSV files.

**Required Columns:**
- `ASIN` - Amazon product identifier
- `Brand` - Brand name
- `Price` or `Price  ₹` - Product price
- `Revenue` - Monthly revenue estimate
- `Sales` - Monthly units sold
- `Review Count` - Number of reviews
- `Ratings` - Star rating (1-5)

#### Magnet Data (Optional but Recommended)
Export keyword data from Helium 10 Magnet as CSV files.

**Required Columns:**
- `Keyword Phrase` - Search term
- `Search Volume` - Monthly searches
- `Search Volume Trend` - Percentage change
- `Competing Products` - Number of competing listings
- `Magnet IQ Score` - Helium 10's relevance score
- `CPR` - 8-day giveaway number

**File Naming Tip**: Use consistent names for automatic matching:
- `xray_laptop_stand.csv` + `magnet_laptop_stand.csv`
- `yoga_mat_xray.csv` + `yoga_mat_magnet.csv`

### Step 2: Upload Files

1. **X-Ray Files** (Required): Upload one or more CSV files
2. **Magnet Files** (Optional): Upload matching keyword CSV files
3. Click **"Process Files"** to analyze

The app automatically matches files by extracting the subcategory name from filenames.

### Step 3: Review Results

#### Comparison Table
Shows all subcategories ranked by score percentage:
- Market size and concentration
- Competition indicators
- Search volume and trend (if Magnet data)
- Demand/Supply ratio (if Magnet data)
- Flag counts (RED/YELLOW/GREEN)
- Action recommendation and risk level

#### Detailed View
For each subcategory:

1. **Recommendation Banner**: Action (STRONG_GO/PROCEED/RISKY/SKIP) with reasoning
2. **Viability Score Card**: Total score breakdown by category
3. **Demand Analysis** (if Magnet data):
   - Primary keyword metrics (volume, trend, competitors)
   - Demand/Supply ratio and verdict
   - Top 5 related keywords
4. **Flags & Signals**: Categorized opportunity indicators
5. **Market Metrics** (X-Ray):
   - Market size and concentration
   - Top seller analysis
   - Top 10 products table
   - Price segment distribution

### Step 4: Export Results

- **CSV (Simple)**: Quick comparison table
- **Excel (Full Report)**: 4-sheet comprehensive analysis with:
  - Rankings sorted by score
  - All metrics in one place
  - Keyword analysis (if Magnet data)
  - Action plan with priority ranking (only GO/PROCEED items)

## Scoring System

### Without Magnet Data (0-100 points)

#### 1. Market Size (20 pts)
- >₹20L: 20 pts | ₹10-20L: 15 pts | ₹5-10L: 10 pts | <₹5L: 5 pts

#### 2. Market Fragmentation (20 pts)
- Top 3 <30%: 20 pts | 30-50%: 15 pts | 50-70%: 10 pts | >70%: 5 pts

#### 3. Competition Level (15 pts)
- <500 reviews: 15 pts | 500-1K: 12 pts | 1K-3K: 8 pts | >3K: 3 pts

#### 4. Customer Satisfaction (15 pts)
- 3.8-4.1★: 15 pts | 4.1-4.3★: 10 pts | >4.3★: 5 pts | <3.8★: 10 pts

#### 5. Price Viability (10 pts)
- >₹500: 10 pts | ₹300-500: 7 pts | <₹300: 4 pts

### With Magnet Data (+50 points = 0-150 total)

#### 6. Demand Score (25 pts)
- ≥150K: 25 pts | 100-149K: 22 pts | 50-99K: 20 pts
- 30-49K: 17 pts | 15-29K: 14 pts | 5-14K: 10 pts | <5K: 5 pts

#### 7. Supply Balance (25 pts)
- <5K competitors: 25 pts | 5-10K: 20 pts | 10-15K: 17 pts
- 15-20K: 14 pts | 20-30K: 10 pts | >30K: 7 pts

### Score Interpretation
- **85-100%** 🔥 **A+**: Excellent - highly recommended
- **70-84%** ✅ **A**: Good - worth pursuing
- **60-69%** ⚠️ **B**: Risky - proceed with caution
- **<60%** ❌ **C**: Poor - skip

## Demand/Supply Ratio

The D/S ratio shows searches per competitor:

- **>8.0** 🔥 **EXCELLENT**: Huge demand, low supply
- **4.0-8.0** ✅ **GOOD**: Solid opportunity
- **2.0-3.9** ⚠️ **MODERATE**: Balanced market
- **1.0-1.9** ⚠️ **POOR**: Oversupplied
- **<1.0** ❌ **AVOID**: More competitors than demand

## Flag System

### 🚨 RED FLAGS (Deal-Breakers)
- Top seller >5,000 reviews
- Market concentration >75%
- Median price <₹250
- Market size <₹3L
- Search volume <2,000/month
- D/S ratio <1.0
- Trend <-15% (COLLAPSING)

### ⚠️ YELLOW FLAGS (Caution)
- Top seller 3,000-5,000 reviews
- Market concentration 65-75%
- Median price ₹250-350
- Market size ₹3-5L
- Search volume 2K-5K
- D/S ratio 1.0-2.0
- Trend -15% to -5% (DECLINING)

### ✅ GREEN SIGNALS (Opportunities)
- Fragmented market (top 3 <40%)
- Quality gap (avg rating 3.8-4.2)
- Good price point (₹500-1,500)
- D/S ratio >4.0
- Growing market (trend >10%)
- **GOLDMINE**: Volume >50K + ratio >3.0

## Project Structure

```
helium10/
├── app.py                      # Main Streamlit application
├── data_processor.py           # X-Ray CSV parsing and cleaning
├── magnet_processor.py         # Magnet CSV parsing and demand analysis
├── metrics_calculator.py       # Market metrics calculations
├── viability_scorer.py         # 150-point scoring system
├── flag_generator.py           # Automated flag system
├── excel_exporter.py           # Multi-sheet Excel export
├── requirements.txt            # Python dependencies
├── test_magnet_integration.py  # Integration tests
└── README.md                   # This file
```

## Example Workflow

1. Export X-Ray data for 10 subcategories → Save as `xray_productname.csv`
2. Export Magnet data for same keywords → Save as `magnet_productname.csv`
3. Upload all files to the app
4. Review comparison table sorted by score
5. Click top opportunities for detailed analysis
6. Check flags & recommendation
7. Export Excel report for further analysis
8. Focus on STRONG_GO and PROCEED items from Action Plan sheet

## Troubleshooting

### File Not Matching
- Ensure file names have consistent format
- The app extracts keywords from filenames automatically
- Example: `IN_AMAZON_magnet__2025-12-04_yoga mat.csv` → extracts "yoga mat"

### Missing Magnet Columns
- Magnet exports must include: Keyword Phrase, Search Volume, Trend, Competing Products
- Re-export from Helium 10 if columns are missing

### Data Quality Warnings
- **<10 products**: X-Ray export incomplete
- **<50 keywords**: Magnet export incomplete
- **Zero search volume**: Invalid Magnet data
- These warnings don't stop analysis but indicate data quality issues

### Excel Export Issues
- Requires `openpyxl` library (included in requirements.txt)
- If export fails, try downloading CSV instead

## Advanced Usage

### Custom Scoring Weights

Edit [viability_scorer.py](viability_scorer.py):

```python
def calculate_viability_score(metrics, magnet_metrics=None):
    # Adjust point allocations
    size_score, _ = score_market_size(market_size)  # Max 20 pts
    # Modify thresholds in individual scoring functions
```

### Custom Flag Thresholds

Edit [flag_generator.py](flag_generator.py):

```python
def generate_flags(xray_metrics, magnet_metrics, demand_supply, scores):
    # Adjust thresholds for flags
    if market_size < 300000:  # Change this value
        red_flags.append(...)
```

### File Matching Logic

Edit [app.py](app.py) - `extract_subcategory_from_filename()` function to handle custom naming patterns.

## Dependencies

```
streamlit==1.32.0          # Web framework
pandas==2.2.0              # Data manipulation
plotly==5.19.0             # Interactive charts
openpyxl==3.1.2            # Excel export
```

## Sample Results

**Yoga Mat Example:**
- Search Volume: 122,840/month (+42% trend 🔥)
- Competing Products: 30,000
- D/S Ratio: 4.09 (GOOD ✅)
- Verdict: Strong demand in saturated market - differentiation opportunity

**Laptop Stand Example:**
- Search Volume: 180,045/month (+2% trend)
- Competing Products: 20,000
- D/S Ratio: 9.0 (EXCELLENT 🔥)
- Verdict: Excellent opportunity with high demand and manageable competition

## Tips for Success

1. **Use Both Data Sources**: Magnet data adds 50% more scoring accuracy
2. **File Naming**: Keep consistent naming for automatic matching
3. **Multiple Categories**: Upload 10-20 to find best opportunities
4. **Trust the Flags**: RED flags are deal-breakers, GREEN are go signals
5. **Check Action Plan Sheet**: Excel export prioritizes best opportunities
6. **Verify on Amazon**: Always confirm top products manually
7. **Track Trends**: Re-export monthly to catch growing markets

## Known Limitations

- Magnet data must be from same marketplace as X-Ray (e.g., both India)
- Seed keyword detection works best with clean filenames
- Very new products (<30 days) may have incomplete data
- Seasonal trends not captured in single snapshot

## Future Roadmap

Upcoming features:
- Historical trend tracking (compare multiple exports)
- Profit calculator with FBA fees
- BSR (Best Seller Rank) integration
- Competitor monitoring alerts
- AI-powered opportunity scoring
- Direct Helium 10 API integration

## License

This project is provided as-is for personal and commercial use.

## Support

For issues or questions:
1. Review this README and troubleshooting section
2. Check [SAMPLE_CSV_STRUCTURE.md](SAMPLE_CSV_STRUCTURE.md) for format details
3. Run [test_magnet_integration.py](test_magnet_integration.py) to verify setup

---

**Built for Amazon FBA sellers. Happy Product Hunting! 🚀📊**
