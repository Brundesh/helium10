# Sample CSV Structure for Helium 10 Xray Exports

This document describes the expected CSV file format for the Amazon FBA Product Opportunity Analyzer.

## Required Columns

The following columns **must** be present in your CSV file:

| Column Name | Data Type | Description | Example Values |
|------------|-----------|-------------|----------------|
| `ASIN` | String | Amazon Standard Identification Number | B08L5WHKBL, B09TZ3M4ND |
| `Brand` | String | Brand or manufacturer name | Nike, Generic, AmazonBasics |
| `Price` or `Price  ₹` | Number/String | Product price in ₹ (may include commas) | 599, 1,299, ₹499 |
| `Revenue` | Number/String | Estimated monthly revenue (may include commas) | 50000, 1,25,000 |
| `Sales` | Number/String | Estimated monthly units sold | 100, 250, 1,500 |
| `Review Count` | Number/String | Total number of customer reviews | 45, 1,200, 3,500 |
| `Ratings` | Number | Average star rating (1-5) | 3.8, 4.2, 4.5 |

## Optional Columns

These columns are recognized but not required:

| Column Name | Description |
|------------|-------------|
| `Product Details` | Product title or description |
| `Image` | Product image URL |
| `Category` | Product category |
| `BSR` | Best Seller Rank |

## Sample CSV Format

Here's an example of what your CSV file should look like:

```csv
ASIN,Brand,Price  ₹,Revenue,Sales,Review Count,Ratings,Product Details
B08L5WHKBL,Nike,1299,2,50,000,192,523,4.3,"Nike Men's Running Shoes"
B09TZ3M4ND,Adidas,1499,2,00,000,134,412,4.2,"Adidas Sports T-Shirt"
B07HXDP123,Puma,899,1,75,000,195,287,4.4,"Puma Gym Bag"
B08K5MNO89,Generic,599,1,50,000,251,156,3.9,"Generic Fitness Band"
B09WXY7890,Reebok,1199,1,25,000,104,342,4.1,"Reebok Training Shorts"
```

## Data Format Notes

### Price Format

The app handles various price formats:
- `599` - Plain number
- `1,299` - With commas
- `₹599` - With currency symbol
- `1,299.00` - With decimals

All formats are automatically cleaned and converted to numbers.

### Revenue Format

Revenue can be formatted as:
- `50000` - Plain number
- `50,000` - With commas
- `1,25,000` - Indian numbering (lakhs)
- `N/A` - Missing data (converted to 0)

### Missing Data

The app handles missing data gracefully:
- Empty cells → Converted to 0
- `N/A`, `NA`, `-` → Converted to 0
- Invalid numbers → Converted to 0

Rows with zero revenue are automatically filtered out.

## Column Name Variations

The app recognizes various column name formats (case-insensitive):

### Price Column
- `Price`
- `Price  ₹` (with spaces and currency)
- `Price (₹)`
- `price`

### Revenue Column
- `Revenue`
- `Monthly Revenue`
- `revenue`
- `REVENUE`

### Review Count Column
- `Review Count`
- `Reviews`
- `Total Reviews`
- `Number of Reviews`

### Ratings Column
- `Ratings`
- `Rating`
- `Star Rating`
- `Average Rating`

## Data Quality Tips

### 1. Remove Invalid Rows

Before uploading, remove rows with:
- Test data
- Placeholder values
- Obviously wrong prices (e.g., ₹1 or ₹100,000)
- Zero or negative values

### 2. Check for Duplicates

The app removes duplicate ASINs automatically (keeps first occurrence), but it's better to clean duplicates beforehand.

### 3. Verify Numeric Columns

Ensure numeric columns contain valid numbers:
- No text in Price/Revenue/Sales columns
- Use commas correctly (1,000 not 1.000)
- No currency symbols mixed with numbers (the app handles this, but clean data is better)

### 4. Consistent Formatting

- Use same currency throughout (₹)
- Use consistent date format if including dates
- Keep brand names consistent (don't mix "Nike" and "NIKE")

## Creating a Sample CSV for Testing

If you want to test the app without Helium 10 data, create a CSV with this structure:

```csv
ASIN,Brand,Price  ₹,Revenue,Sales,Review Count,Ratings,Product Details
TEST001,TestBrand1,500,100000,200,150,4.2,"Test Product 1"
TEST002,TestBrand2,750,90000,120,280,4.0,"Test Product 2"
TEST003,TestBrand3,600,85000,142,95,4.3,"Test Product 3"
TEST004,TestBrand4,450,75000,167,420,3.9,"Test Product 4"
TEST005,TestBrand5,800,70000,88,310,4.1,"Test Product 5"
TEST006,TestBrand6,550,65000,118,180,4.2,"Test Product 6"
TEST007,TestBrand7,700,60000,86,250,4.0,"Test Product 7"
TEST008,TestBrand8,650,55000,85,140,4.4,"Test Product 8"
TEST009,TestBrand9,500,50000,100,380,3.8,"Test Product 9"
TEST010,TestBrand10,900,45000,50,520,4.2,"Test Product 10"
```

Save this as `test_product.csv` and upload to the app.

## Exporting from Helium 10 Xray

To get the correct CSV format from Helium 10:

1. Open Helium 10 Chrome Extension
2. Navigate to Amazon product search results
3. Click "X-Ray" button
4. Wait for analysis to complete
5. Click "Export" or download icon
6. Select "CSV" format
7. Save file with descriptive name (e.g., `yoga_mats.csv`)

## File Naming Best Practices

Use descriptive filenames for your CSV exports:

✅ **Good Examples:**
- `yoga_mats.csv`
- `resistance_bands.csv`
- `protein_shaker_bottles.csv`
- `gym_gloves.csv`

❌ **Avoid:**
- `export1.csv`
- `data.csv`
- `untitled.csv`
- `new_file.csv`

The filename (without .csv extension) is used as the product name in the comparison table.

## Troubleshooting CSV Issues

### Error: "Missing required columns"

**Problem**: CSV doesn't have all required columns.

**Solution**:
1. Open CSV in spreadsheet software
2. Check column headers match required names
3. Add missing columns or rename existing ones
4. Save and re-upload

### Error: "Error processing CSV file"

**Problem**: CSV is corrupted or improperly formatted.

**Solution**:
1. Open in text editor to check for formatting issues
2. Ensure proper comma separation
3. Check for special characters in data
4. Re-export from Helium 10 if needed

### Warning: "Invalid data structure"

**Problem**: Required columns exist but have no valid data.

**Solution**:
1. Check that numeric columns contain numbers
2. Verify ASINs are present
3. Ensure at least some products have revenue > 0
4. Remove rows with all zeros or N/A values

### No Products Showing After Upload

**Problem**: All data filtered out as invalid.

**Solution**:
1. Check Revenue column has values > 0
2. Verify numeric columns contain valid numbers
3. Look for ASINs that might be duplicated
4. Check for formatting issues (e.g., text in number columns)

## CSV Character Encoding

If you see garbled text or special characters:

1. Open CSV in text editor (Notepad++, VS Code, etc.)
2. Save as UTF-8 encoding
3. Re-upload to app

Most modern exports from Helium 10 use UTF-8 by default.

## Maximum File Size

- Recommended: Up to 1,000 products per CSV
- Maximum tested: 5,000 products per CSV
- Multiple files: No hard limit, but 20-30 files recommended for performance

Larger files take longer to process but should work fine.

---

**Questions about CSV format?** Check that your export matches the structure above. The app is flexible with minor variations but requires the core columns listed.
