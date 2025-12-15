# TogoMCP Automated Evaluation Toolkit - Installation Summary

## 📦 What Was Created

The following files have been created in `/Users/arkinjo/work/GitHub/togo-mcp/evaluation/scripts/`:

### Core Scripts

1. **`automated_test_runner.py`** (450+ lines)
   - Main evaluation script
   - Runs questions against baseline (no tools) and TogoMCP (with tools)
   - Captures responses, timing, tool usage, and token counts
   - Exports results to CSV or JSON
   - Includes retry logic, progress tracking, and intermediate saves
   - Full-featured command-line interface

2. **`results_analyzer.py`** (350+ lines)
   - Analyzes CSV results from test runner
   - Provides summary statistics
   - Breaks down results by category
   - Analyzes tool usage patterns
   - Identifies failures
   - Compares baseline vs TogoMCP answers
   - Exports insights to JSON

3. **`setup.py`** (70+ lines)
   - Makes scripts executable (Unix/Linux/Mac)
   - Verifies dependencies
   - Checks API key
   - Validates file presence

### Supporting Files

4. **`example_questions.json`**
   - 10 example questions across all 6 categories
   - Demonstrates proper question format
   - Includes expected answers and notes
   - Ready to run as-is for testing

5. **`config.json`**
   - Default configuration for test runner
   - Model selection, token limits, temperature
   - System prompts for baseline and TogoMCP
   - Timeout and retry settings

6. **`requirements.txt`**
   - Python dependencies (just `anthropic>=0.40.0`)

7. **`quick_start.sh`**
   - One-command setup and execution
   - Checks dependencies
   - Runs example evaluation
   - Bash script for quick demos

### Documentation

8. **`README.md`** (500+ lines)
   - Complete documentation
   - Installation instructions
   - Usage examples
   - Question file format
   - Configuration options
   - Output format explanation
   - Advanced usage
   - Troubleshooting guide
   - Best practices

9. **`QUICK_REFERENCE.md`** (250+ lines)
   - One-page quick reference
   - Common commands
   - Templates
   - Workflow examples
   - Troubleshooting tips
   - Useful one-liners

## 🚀 Quick Start

### Option 1: Automated Setup

```bash
cd /Users/arkinjo/work/GitHub/togo-mcp/evaluation/scripts/

# Run setup
python setup.py

# Set API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Install dependencies
pip install -r requirements.txt

# Run example evaluation
python automated_test_runner.py example_questions.json

# Analyze results
python results_analyzer.py evaluation_results.csv
```

### Option 2: Quick Start Script

```bash
cd /Users/arkinjo/work/GitHub/togo-mcp/evaluation/scripts/

# Set API key first
export ANTHROPIC_API_KEY="your-api-key-here"

# Run everything at once
./quick_start.sh
```

### Option 3: Manual Step-by-Step

```bash
# 1. Navigate to scripts directory
cd /Users/arkinjo/work/GitHub/togo-mcp/evaluation/scripts/

# 2. Set API key
export ANTHROPIC_API_KEY="your-api-key-here"

# 3. Install dependencies
pip install anthropic

# 4. Run test
python automated_test_runner.py example_questions.json

# 5. View results
open evaluation_results.csv  # Mac
# or
xdg-open evaluation_results.csv  # Linux

# 6. Analyze
python results_analyzer.py evaluation_results.csv
```

## 📊 What the Tools Do

### Automated Test Runner

**Input:**
- JSON file with questions
- Optional: config file

**Process:**
1. Loads questions from JSON
2. For each question:
   - Asks Claude WITHOUT tools (baseline)
   - Asks Claude WITH MCP tools (TogoMCP)
   - Captures responses, timing, tool usage
3. Saves results to CSV after every 5 questions
4. Prints progress and summary

**Output:**
- CSV file with detailed results
- Includes text responses, timing, tokens, tools used
- One row per question
- Compatible with evaluation tracker format

### Results Analyzer

**Input:**
- CSV file from test runner

**Process:**
1. Loads CSV data
2. Calculates statistics
3. Groups by category
4. Identifies tool usage patterns
5. Finds failures
6. Compares answers

**Output:**
- Console report with statistics
- Optional: JSON file with insights
- Summary by category
- Tool usage analysis
- Failure identification

## 🎯 Next Steps

### 1. Test the Installation (5 min)

```bash
cd /Users/arkinjo/work/GitHub/togo-mcp/evaluation/scripts/
export ANTHROPIC_API_KEY="your-key"
python automated_test_runner.py example_questions.json
```

Expected output:
- Progress messages for 10 questions
- `evaluation_results.csv` file created
- Summary statistics printed

### 2. Review Example Results (10 min)

```bash
# Analyze the results
python results_analyzer.py evaluation_results.csv

# Open in spreadsheet
open evaluation_results.csv
```

Look for:
- Which questions used tools
- Response time differences
- Answer quality differences

### 3. Create Your First Custom Questions (20 min)

```bash
# Copy and edit example
cp example_questions.json my_questions.json
nano my_questions.json  # or your preferred editor
```

Design 3-5 questions that:
- Test specific TogoMCP capabilities
- Have verifiable expected answers
- Cover different categories
- Are realistic research questions

### 4. Run Your Evaluation (varies)

```bash
# Test your questions
python automated_test_runner.py my_questions.json -o my_results.csv

# Analyze
python results_analyzer.py my_results.csv -v
```

### 5. Add Manual Scoring (30 min)

Open `my_results.csv` and add columns:
- `Accuracy` (0-3)
- `Precision` (0-3)
- `Completeness` (0-3)
- `Verifiability` (0-3)
- `Currency` (0-3)
- `Impossibility` (0-3)
- `Total_Score` (sum)
- `Assessment` (CRITICAL/VALUABLE/MARGINAL/REDUNDANT)
- `Include` (YES/NO)

Use the rubric from `../togomcp_evaluation_rubric.md`

## 📁 File Structure

```
evaluation/
├── scripts/                          # NEW automated tools
│   ├── automated_test_runner.py      # Main evaluation script
│   ├── results_analyzer.py           # Results analysis tool
│   ├── example_questions.json        # Sample questions
│   ├── config.json                   # Default configuration
│   ├── requirements.txt              # Python dependencies
│   ├── quick_start.sh               # Quick start script
│   ├── setup.py                      # Setup verification
│   ├── README.md                     # Full documentation
│   ├── QUICK_REFERENCE.md            # Quick reference
│   └── INSTALLATION_SUMMARY.md       # This file
├── EVALUATION_README.md              # Existing: Overview of evaluation suite
├── togomcp_evaluation_rubric.md      # Existing: Scoring methodology
├── togomcp_evaluation_template.md    # Existing: Full evaluation template
├── togomcp_quick_eval_form.md        # Existing: Quick eval form
├── togomcp_evaluation_tracker.csv    # Existing: Tracking spreadsheet
└── togomcp_evaluation_tracker.md     # Existing: Tracker documentation
```

## 🔗 Integration with Existing Evaluation Framework

The automated tools complement the existing manual evaluation framework:

**Existing Framework** (Manual):
- Rubric with 6 scoring dimensions
- Detailed evaluation template
- Quick eval form
- CSV tracker

**New Tools** (Automated):
- Automated question running
- Automatic data collection
- Batch processing
- Results analysis

**Combined Workflow**:
1. **Design questions** using existing rubric
2. **Run automated tests** to collect data
3. **Analyze results** with analyzer tool
4. **Add manual scores** using rubric
5. **Track in CSV** with existing tracker

## 💡 Key Features

### Test Runner Features
- ✅ Automatic baseline vs TogoMCP comparison
- ✅ Tool usage tracking
- ✅ Response timing measurement
- ✅ Token usage tracking
- ✅ Retry logic for failures
- ✅ Progress tracking
- ✅ Intermediate saves every 5 questions
- ✅ Interrupt handling (Ctrl+C safe)
- ✅ CSV and JSON export
- ✅ Configurable prompts and settings

### Analyzer Features
- ✅ Summary statistics
- ✅ Category breakdown
- ✅ Tool usage analysis
- ✅ Failure identification
- ✅ Answer comparison
- ✅ Verbose mode for details
- ✅ JSON insights export

## 🎓 Learning Resources

1. **Start Here**: `QUICK_REFERENCE.md`
   - One-page overview
   - Common commands
   - Quick workflows

2. **Deep Dive**: `README.md`
   - Complete documentation
   - All features explained
   - Advanced usage
   - Troubleshooting

3. **Methodology**: `../togomcp_evaluation_rubric.md`
   - Scoring system
   - Question categories
   - Assessment criteria

4. **Examples**: `example_questions.json`
   - See 10 example questions
   - Learn proper format
   - Understand categories

## ⚙️ Configuration Options

### Model Selection
- Default: `claude-sonnet-4-20250514`
- Change in `config.json` for different models

### Prompts
- Baseline prompt: Instructs Claude to use only training knowledge
- TogoMCP prompt: Instructs Claude to use MCP tools

### Timeouts & Retries
- Default timeout: 60 seconds
- Default retries: 3 attempts
- Configurable in `config.json`

### Output Format
- CSV: Compatible with spreadsheets, easy analysis
- JSON: Programmatic access, nested data

## 🔍 Troubleshooting

### "Command not found"
```bash
# Use python or python3
python3 automated_test_runner.py example_questions.json
```

### "Permission denied"
```bash
# Make executable
chmod +x automated_test_runner.py
# Or use python directly
python automated_test_runner.py example_questions.json
```

### "API key not set"
```bash
export ANTHROPIC_API_KEY="your-key"
# Verify
echo $ANTHROPIC_API_KEY
```

### "anthropic not found"
```bash
pip install anthropic
# Or
pip install -r requirements.txt
```

## 📞 Support

- **Documentation**: See `README.md` for detailed docs
- **Quick Help**: See `QUICK_REFERENCE.md`
- **Examples**: Check `example_questions.json`
- **Issues**: Review error messages carefully
- **Command Help**: Run with `-h` flag

## ✅ Verification Checklist

Before starting your evaluation:

- [ ] Python 3.11+ installed
- [ ] `pip` working
- [ ] API key set in environment
- [ ] `anthropic` package installed
- [ ] All scripts present in directory
- [ ] Example questions run successfully
- [ ] Results CSV generated and viewable
- [ ] Analyzer runs without errors

## 🎉 You're Ready!

You now have a complete automated evaluation toolkit for TogoMCP. The tools will:

1. **Save time**: Automate the repetitive parts
2. **Ensure consistency**: Same process for every question
3. **Capture data**: Comprehensive metrics automatically
4. **Enable analysis**: Built-in statistics and insights
5. **Scale easily**: Run 10 or 100 questions with same effort

Happy evaluating! 🚀

---

**Created**: 2025-12-15  
**Version**: 1.0  
**Location**: `/Users/arkinjo/work/GitHub/togo-mcp/evaluation/scripts/`
