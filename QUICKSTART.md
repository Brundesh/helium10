# Quick Start Guide

Get up and running with the Amazon FBA Product Opportunity Analyzer in 5 minutes!

## 1. Installation (2 minutes)

```bash
# Navigate to the project directory
cd helium10

# Install dependencies
pip install -r requirements.txt
```

## 2. Run the App (30 seconds)

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 3. Test with Sample Data (1 minute)

Want to try it out before using your own data?

1. Look for the `sample_data.csv` file in this directory
2. In the app sidebar, click "Browse files"
3. Upload `sample_data.csv`
4. Click "Process Files"
5. Explore the results!

## 4. Use Your Own Data (2 minutes)

### Export from Helium 10:
1. Open Helium 10 X-Ray on any Amazon search results page
2. Click the Export/Download button
3. Select CSV format
4. Save with a descriptive name (e.g., `yoga_mats.csv`)

### Upload to App:
1. Click "Browse files" in the sidebar
2. Select one or more CSV files
3. Click "Process Files"
4. View your product analysis!

## What You'll See

### Comparison Table
- All products ranked by viability score
- Key metrics at a glance
- Color-coded recommendations

### Detailed Analysis
- Select any product to see:
  - Score breakdown
  - Top 10 products
  - Price segment analysis
  - Revenue charts

### Export
- Download comparison table as CSV
- Use for presentations or further analysis

## Quick Tips

✅ **Do This:**
- Upload 10-20 product categories for best comparison
- Use recent Helium 10 exports (< 1 week old)
- Name files descriptively (product_name.csv)
- Review detailed analysis for top 3 products

❌ **Avoid This:**
- Don't upload files with missing columns
- Don't use very old data (> 1 month)
- Don't skip the detailed view - it has valuable insights!
- Don't ignore products with scores 60-69 (they might still work with good execution)

## Understanding Your Results

### Score > 85 🔥
**Action**: Strong opportunity - proceed with product research
- Large market with room for new sellers
- Good margins and manageable competition

### Score 70-84 ✅
**Action**: Good opportunity - validate with deeper research
- Solid fundamentals
- May require better differentiation

### Score 60-69 ⚠️
**Action**: Risky - only proceed if you have unique advantage
- Some challenging factors
- Needs strong differentiation or better pricing

### Score < 60 ❌
**Action**: Skip - find better opportunities
- Multiple red flags
- Better products available

## Next Steps After Analysis

1. **For Top Products (Score > 85):**
   - Check actual Amazon listings
   - Analyze competitor products
   - Calculate profit margins
   - Research suppliers
   - Validate market assumptions

2. **For Good Products (Score 70-84):**
   - Identify differentiation opportunities
   - Check if you can improve on weaknesses
   - Calculate break-even point
   - Assess competition strategy

3. **For All Products:**
   - Export comparison table
   - Share with team/partners
   - Track over time (re-run monthly)
   - Document decision rationale

## Troubleshooting

### App won't start?
```bash
# Check if streamlit is installed
pip list | grep streamlit

# Reinstall if needed
pip install -r requirements.txt --force-reinstall
```

### CSV upload error?
- Verify CSV has required columns (see SAMPLE_CSV_STRUCTURE.md)
- Open in Excel/Sheets and check for missing data
- Try the sample_data.csv file first

### Slow performance?
- Limit to 20-30 products at once
- Close other browser tabs
- Reduce CSV file size (top 100 products per category)

## Pro Tips

### 1. Batch Analysis
Upload all product CSVs at once for faster analysis:
- Prepare 20 CSV files
- Select all in file picker
- Process once
- Compare all at once

### 2. Regular Monitoring
Track product opportunities over time:
- Export data monthly
- Re-run analysis
- Look for trends (improving/declining)
- Adjust strategy based on changes

### 3. Combination Strategy
Don't just look at top scorer:
- Top 3 products might serve different markets
- Consider portfolio approach
- Balance high/medium risk opportunities
- Factor in your unique strengths

### 4. Deep Dive Analysis
For top candidates:
1. Export detailed view data
2. Manually check top 10 products on Amazon
3. Read negative reviews (opportunity signals)
4. Check BSR trends (Jungle Scout/Keepa)
5. Validate supplier availability

## Getting Help

- **CSV Format Issues**: Read SAMPLE_CSV_STRUCTURE.md
- **Understanding Scores**: Read README.md scoring section
- **Technical Problems**: Check error messages in app

## What's Next?

Once you've identified good opportunities:

1. **Validate Demand**: Use Helium 10 keyword tools
2. **Check Competition**: Analyze top 10 listings in detail
3. **Calculate Margins**: Factor in all costs (product, shipping, Amazon fees)
4. **Source Products**: Contact suppliers, order samples
5. **Test Market**: Consider small initial order
6. **Track Results**: Monitor sales and adjust

---

## Sample Workflow

Here's how a typical session might look:

```
Morning: Export 15 product ideas from Helium 10
├─ 10:00 AM - Upload all CSVs to app
├─ 10:05 AM - Review comparison table
├─ 10:10 AM - Deep dive into top 3 products
├─ 10:30 AM - Export results
└─ 10:35 AM - Share with team

Afternoon: Research top 2 products further
├─ 2:00 PM - Check Amazon listings
├─ 2:30 PM - Research suppliers
├─ 3:00 PM - Calculate profit margins
└─ 3:30 PM - Make go/no-go decision
```

---

**Ready to find your next winning product? Let's go! 🚀**

Run `streamlit run app.py` and start analyzing!
