#!/bin/bash
# Quick Start Script for TogoMCP Evaluation

set -e

echo "====================================="
echo "TogoMCP Evaluation Quick Start"
echo "====================================="
echo ""

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY environment variable not set"
    echo ""
    echo "Please set your API key:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    exit 1
fi

echo "✓ API key found"

# Check if anthropic package is installed
if ! python3 -c "import anthropic" 2>/dev/null; then
    echo ""
    echo "📦 Installing required package: anthropic"
    pip install -r requirements.txt
else
    echo "✓ Required packages installed"
fi

echo ""
echo "Running evaluation with example questions..."
echo ""

# Run the test runner
python3 automated_test_runner.py example_questions.json

echo ""
echo "====================================="
echo "Evaluation Complete!"
echo "====================================="
echo ""
echo "Results saved to: evaluation_results.csv"
echo ""
echo "Next steps:"
echo "  1. Review results: open evaluation_results.csv"
echo "  2. Analyze results: python3 results_analyzer.py evaluation_results.csv"
echo "  3. Create your own questions: edit example_questions.json"
echo ""
