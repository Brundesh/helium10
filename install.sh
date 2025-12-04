#!/bin/bash
# Installation script for Amazon FBA Product Opportunity Analyzer

echo "=================================================="
echo "Amazon FBA Product Opportunity Analyzer"
echo "Installation Script"
echo "=================================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.8 or higher first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed!"
    echo "Please install pip first."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Dependencies installed successfully!"
else
    echo ""
    echo "❌ Failed to install dependencies!"
    exit 1
fi

echo ""
echo "=================================================="
echo "🎉 Installation complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Run: streamlit run app.py"
echo "  2. Upload sample_data.csv to test the app"
echo "  3. Upload your Helium 10 CSV exports"
echo ""
echo "For help, read:"
echo "  - QUICKSTART.md (5-minute guide)"
echo "  - README.md (complete documentation)"
echo ""
echo "To verify setup: python3 verify_setup.py"
echo "=================================================="
