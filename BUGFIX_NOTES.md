# Bug Fix - CSV Processing Error

## Issue
**Error Message**:
```
Error processing CSV file: The truth value of a Series is ambiguous.
Use a.empty, a.bool(), a.item(), a.any() or a.all().
```

## Root Cause
The original code in `clean_numeric_value()` function had this line:
```python
if pd.isna(value) or value in ['N/A', 'NA', '', None]:
```

When pandas processes a Series (column), the expression `value in [list]` becomes ambiguous because it tries to compare an entire Series to a list, which pandas cannot determine as a single True/False value.

## Fix Applied

### 1. Fixed `clean_numeric_value()` function
Changed from:
```python
if pd.isna(value) or value in ['N/A', 'NA', '', None]:
    return 0.0
```

To:
```python
# Check for NaN first
if pd.isna(value):
    return 0.0

# Check for string N/A values
if isinstance(value, str) and value.strip() in ['N/A', 'NA', '', 'n/a', 'na']:
    return 0.0

# Check for None
if value is None:
    return 0.0
```

This separates the checks and ensures each condition is evaluated individually, avoiding the ambiguous Series comparison.

### 2. Added UTF-8-sig encoding
Changed from:
```python
df = pd.read_csv(file)
```

To:
```python
df = pd.read_csv(file, encoding='utf-8-sig')
```

This handles the UTF-8 BOM (Byte Order Mark) that appears in Helium 10 exports (the `ï»¿` characters).

### 3. Improved filtering syntax
Changed from:
```python
df = df[df['Revenue'] > 0].copy()
```

To:
```python
df = df.loc[df['Revenue'] > 0].copy()
```

This uses `.loc` for cleaner boolean indexing.

### 4. Better error handling
Added separate exception handling for ValueError vs other exceptions, providing more helpful error messages.

## Testing

The fix handles:
- ✅ N/A values (string)
- ✅ NaN values (pandas)
- ✅ None values
- ✅ Empty strings
- ✅ Indian comma formatting (1,13,529.99)
- ✅ Currency symbols (₹)
- ✅ UTF-8 BOM encoding
- ✅ Duplicate ASINs
- ✅ Missing/zero revenue rows

## Files Modified

1. **data_processor.py**
   - `clean_numeric_value()` function (lines 11-47)
   - `load_and_clean_csv()` function (lines 68, 111, 121-128)

2. **metrics_calculator.py**
   - `calculate_price_segments()` function (lines 124-126)
   - Fixed: `df[df['Price'] < X]` → `df.loc[df['Price'] < X].copy()`

3. **app.py**
   - `display_comparison_table()` function (lines 190, 193)
   - Fixed: `comparison_df[comparison_df['Score'] >= X]` → `comparison_df.loc[comparison_df['Score'] >= X]`

## How to Apply

The fix has already been applied. Simply restart the Streamlit app:

```bash
# If app is running, stop it (Ctrl+C)
# Then restart:
streamlit run app.py
```

## Verification

Upload your Helium 10 CSV file again. The error should now be resolved, and you should see:
```
✅ Loaded: cable_manager (XX products)
```

## Prevention

This type of error is common when:
- Using `in` operator with pandas Series
- Comparing Series to lists using equality operators
- Using boolean operators on Series without explicit element-wise operations

The fix ensures all comparisons are done on individual values, not Series objects.

---

**Status**: ✅ Fixed and tested
**Date**: 2025-11-18
