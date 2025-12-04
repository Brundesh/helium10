#!/usr/bin/env python3
"""
Setup verification script for Amazon FBA Product Opportunity Analyzer.
Run this script to verify all dependencies are installed correctly.
"""

import sys
import os

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.8 or higher")
        return False

def check_dependencies():
    """Check if all required packages are installed."""
    print("\nChecking dependencies...")
    required = {
        'streamlit': '1.32.0',
        'pandas': '2.2.0',
        'plotly': '5.19.0',
        'openpyxl': '3.1.2'
    }

    missing = []
    installed = []

    for package, version in required.items():
        try:
            __import__(package)
            installed.append(f"✅ {package}")
        except ImportError:
            missing.append(f"❌ {package}")

    for item in installed:
        print(item)

    for item in missing:
        print(item)

    if missing:
        print("\n⚠️  Some dependencies are missing!")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True

def check_project_files():
    """Check if all required project files exist."""
    print("\nChecking project files...")
    required_files = [
        'app.py',
        'data_processor.py',
        'metrics_calculator.py',
        'viability_scorer.py',
        'requirements.txt',
        'README.md',
        'QUICKSTART.md',
        'SAMPLE_CSV_STRUCTURE.md',
        'sample_data.csv'
    ]

    missing = []
    found = []

    for file in required_files:
        if os.path.exists(file):
            found.append(f"✅ {file}")
        else:
            missing.append(f"❌ {file}")

    for item in found:
        print(item)

    for item in missing:
        print(item)

    if missing:
        print("\n⚠️  Some project files are missing!")
        return False
    else:
        print("\n✅ All project files present!")
        return True

def test_imports():
    """Test if custom modules can be imported."""
    print("\nTesting module imports...")
    try:
        import data_processor
        print("✅ data_processor")
    except Exception as e:
        print(f"❌ data_processor: {e}")
        return False

    try:
        import metrics_calculator
        print("✅ metrics_calculator")
    except Exception as e:
        print(f"❌ metrics_calculator: {e}")
        return False

    try:
        import viability_scorer
        print("✅ viability_scorer")
    except Exception as e:
        print(f"❌ viability_scorer: {e}")
        return False

    print("\n✅ All modules import successfully!")
    return True

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Amazon FBA Product Opportunity Analyzer")
    print("Setup Verification Script")
    print("=" * 60)

    checks = [
        check_python_version(),
        check_project_files(),
        check_dependencies(),
    ]

    if all(checks):
        print("\n" + "=" * 60)
        print("🎉 Setup verification complete - all checks passed!")
        print("=" * 60)
        print("\nYou're ready to go!")
        print("\nNext steps:")
        print("  1. Run: streamlit run app.py")
        print("  2. Upload sample_data.csv to test")
        print("  3. Upload your Helium 10 CSV exports")
        print("\nFor help, read QUICKSTART.md")
        print("=" * 60)
        test_imports()
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Setup verification failed!")
        print("=" * 60)
        print("\nPlease fix the issues above and run again.")
        print("\nFor installation help, read README.md")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
