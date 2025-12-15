# TogoMCP Evaluation Toolkit - Quick Reference

## File Overview

```
evaluation/scripts/
├── automated_test_runner.py  # Main evaluation script
├── results_analyzer.py        # Results analysis tool
├── example_questions.json     # Sample questions (10 examples)
├── config.json                # Default configuration
├── requirements.txt           # Python dependencies
├── quick_start.sh            # Quick start script
├── README.md                 # Detailed documentation
└── QUICK_REFERENCE.md        # This file
```

## 30-Second Start

```bash
# 1. Set API key
export ANTHROPIC_API_KEY="your-key"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run example
python automated_test_runner.py example_questions.json

# 4. Analyze results
python results_analyzer.py evaluation_results.csv
```

## Common Commands

### Run Evaluation

```bash
# Basic
python automated_test_runner.py questions.json

# With custom config
python automated_test_runner.py questions.json -c my_config.json

# Custom output path
python automated_test_runner.py questions.json -o results.csv

# JSON output
python automated_test_runner.py questions.json --format json -o results.json
```

### Analyze Results

```bash
# Standard analysis
python results_analyzer.py results.csv

# Verbose (shows answer comparisons)
python results_analyzer.py results.csv -v

# Export insights to JSON
python results_analyzer.py results.csv -o insights.json
```

## Question File Template

```json
[
  {
    "id": 1,
    "category": "Precision",
    "question": "What is the UniProt ID for human BRCA1?",
    "expected_answer": "P38398",
    "notes": "Basic ID lookup test"
  }
]
```

### Required Fields
- `question`: The question text

### Optional Fields
- `id`: Question number
- `category`: Precision|Completeness|Integration|Currency|Specificity|Structured Query
- `expected_answer`: What you expect
- `notes`: Additional context

## Config File Template

```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 4000,
  "temperature": 1.0,
  "baseline_system_prompt": "Answer using only training knowledge...",
  "togomcp_system_prompt": "Use MCP tools when helpful...",
  "timeout": 60,
  "retry_attempts": 3,
  "retry_delay": 2
}
```

## Output Fields

### CSV Columns

| Column | Description |
|--------|-------------|
| `question_id` | Question identifier |
| `category` | Question category |
| `question_text` | Full question |
| `baseline_text` | Answer without tools |
| `baseline_time` | Response time (seconds) |
| `togomcp_text` | Answer with tools |
| `togomcp_time` | Response time (seconds) |
| `tools_used` | Tools that were called |
| `*_success` | Whether test succeeded |
| `*_error` | Error if failed |
| `*_tokens` | Token usage |

## Typical Workflow

### 1. Design Questions (30 min)
```bash
# Copy example and edit
cp example_questions.json my_questions.json
nano my_questions.json
```

### 2. Test Small Batch (5 min)
```bash
# Create 3-5 test questions first
python automated_test_runner.py test_batch.json
```

### 3. Review & Iterate (15 min)
```bash
# Check results
python results_analyzer.py evaluation_results.csv

# Review CSV in spreadsheet
open evaluation_results.csv
```

### 4. Run Full Evaluation (varies)
```bash
# Run complete question set
python automated_test_runner.py my_questions.json -o full_results.csv
```

### 5. Analyze Results (10 min)
```bash
# Detailed analysis
python results_analyzer.py full_results.csv -v -o insights.json
```

### 6. Manual Scoring (30 min)
```bash
# Open CSV and add rubric scores
# Add columns: Accuracy, Precision, Completeness, etc.
# Score 0-3 for each dimension
```

## Quick Troubleshooting

### Problem: "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY="your-key-here"
# Add to ~/.bashrc or ~/.zshrc for persistence
```

### Problem: "anthropic package not found"
```bash
pip install anthropic
# Or: pip install -r requirements.txt
```

### Problem: Test timing out
Edit `config.json`:
```json
{
  "timeout": 120,  // Increase to 120 seconds
  "retry_attempts": 5  // More retries
}
```

### Problem: Rate limits
```bash
# Split into smaller batches
# Run fewer questions at once
# Add delays between questions
```

## Tips & Tricks

### Interrupt Safely
- Press `Ctrl+C` to stop evaluation
- Partial results are saved
- Resume by excluding completed questions

### Save Costs
- Test with 3-5 questions first
- Use smaller batches
- Review failures before re-running

### Speed Up Analysis
```bash
# Use command-line CSV viewer
column -s, -t < results.csv | less -S

# Quick grep for tools
grep "search_uniprot" results.csv

# Count by category
cut -d, -f3 results.csv | sort | uniq -c
```

### Batch Processing
```bash
# Process in parallel (careful with rate limits!)
python automated_test_runner.py batch1.json -o b1.csv &
python automated_test_runner.py batch2.json -o b2.csv &
wait

# Combine results
cat b*.csv | head -1 > combined.csv  # header
tail -n +2 -q b*.csv >> combined.csv  # data
```

## Best Practices

### ✅ Do This
- Start with 3-5 test questions
- Verify expected answers beforehand
- Use descriptive question IDs
- Document your reasoning in `notes`
- Save intermediate results
- Review failures immediately

### ❌ Avoid This
- Running 100+ questions without testing
- Using vague question text
- Ignoring failure messages
- Skipping the analysis step
- Not backing up results

## Integration with Main Evaluation

The automated results are designed to integrate with the manual evaluation rubric:

1. Run automated tests
2. Export CSV
3. Open in spreadsheet
4. Add rubric scoring columns
5. Use existing evaluation tracker format

## Question Categories Reference

1. **Precision**: Exact IDs, sequences, properties
2. **Completeness**: "List all...", "How many..."
3. **Integration**: Cross-database linking, ID conversion
4. **Currency**: Recent/updated information
5. **Specificity**: Rare diseases, unusual compounds
6. **Structured Query**: Complex filters, SPARQL-like

## Getting Help

- See `README.md` for detailed documentation
- Check example questions in `example_questions.json`
- Review example config in `config.json`
- Run with `-h` flag for help:
  ```bash
  python automated_test_runner.py -h
  python results_analyzer.py -h
  ```

## Useful One-Liners

```bash
# Count successful tests
grep ",True," results.csv | wc -l

# List all tools used
cut -d, -f17 results.csv | tr ',' '\n' | sort -u

# Average response time
awk -F, '{sum+=$14} END {print sum/NR}' results.csv

# Find failures
grep ",False," results.csv

# Questions by category
cut -d, -f3 results.csv | tail -n +2 | sort | uniq -c
```

---

**Last Updated**: 2025-12-15
**Version**: 1.0
