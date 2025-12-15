#!/usr/bin/env python3
"""
Setup script for TogoMCP evaluation tools.
Makes scripts executable and verifies installation.
"""

import os
import sys
from pathlib import Path


def main():
    """Make scripts executable and verify setup."""
    
    # Get script directory
    script_dir = Path(__file__).parent
    
    print("🔧 TogoMCP Evaluation Tools Setup")
    print("=" * 50)
    
    # Scripts to make executable
    scripts = [
        'automated_test_runner.py',
        'results_analyzer.py',
        'quick_start.sh'
    ]
    
    # Make executable (Unix-like systems)
    if sys.platform != 'win32':
        for script in scripts:
            script_path = script_dir / script
            if script_path.exists():
                os.chmod(script_path, 0o755)
                print(f"✓ Made {script} executable")
            else:
                print(f"⚠ {script} not found")
    else:
        print("ℹ On Windows, scripts don't need to be made executable")
    
    # Check for required dependencies
    print("\n📦 Checking dependencies...")
    
    try:
        import anthropic
        print("✓ anthropic package installed")
    except ImportError:
        print("✗ anthropic package not installed")
        print("  Install with: pip install -r requirements.txt")
    
    # Check for API key
    print("\n🔑 Checking API key...")
    if os.environ.get('ANTHROPIC_API_KEY'):
        print("✓ ANTHROPIC_API_KEY is set")
    else:
        print("⚠ ANTHROPIC_API_KEY not set")
        print("  Set with: export ANTHROPIC_API_KEY='your-key-here'")
    
    # Verify files
    print("\n📁 Verifying files...")
    required_files = [
        'automated_test_runner.py',
        'results_analyzer.py',
        'example_questions.json',
        'config.json',
        'requirements.txt',
        'README.md',
        'QUICK_REFERENCE.md'
    ]
    
    all_present = True
    for file in required_files:
        if (script_dir / file).exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} missing")
            all_present = False
    
    print("\n" + "=" * 50)
    if all_present:
        print("✅ Setup complete! All files present.")
        print("\nNext steps:")
        print("1. Set API key: export ANTHROPIC_API_KEY='your-key'")
        print("2. Install deps: pip install -r requirements.txt")
        print("3. Run test: ./automated_test_runner.py example_questions.json")
        print("   or: python automated_test_runner.py example_questions.json")
    else:
        print("⚠ Some files are missing. Please verify the installation.")
    
    print("=" * 50)


if __name__ == '__main__':
    main()
