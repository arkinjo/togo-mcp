# TogoMCP Automated Test Runner

This directory contains scripts for automated evaluation of TogoMCP capabilities.

## Quick Start

### 1. Installation

```bash
# Install required Python package
pip install -r requirements.txt

# Or install with the project dependencies
cd ../..  # Navigate to project root
pip install -e .
```

### 2. Set Up API Key

```bash
# Export your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Or add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
```

### 3. Run Example Evaluation

```bash
# Run the example questions
python automated_test_runner.py example_questions.json

# Results will be saved to evaluation_results.csv
```

## Usage

### Basic Usage

```bash
python automated_test_runner.py <questions_file.json>
```

### Advanced Options

```bash
# Use custom configuration
python automated_test_runner.py questions.json -c custom_config.json

# Specify output path
python automated_test_runner.py questions.json -o my_results.csv

# Export as JSON instead of CSV
python automated_test_runner.py questions.json -o results.json --format json

# Combine options
python automated_test_runner.py questions.json -c config.json -o results.csv
```

### Command-Line Arguments

- `questions_file` (required): Path to JSON file containing questions
- `-c, --config`: Path to configuration JSON file (optional)
- `-o, --output`: Output path for results (default: `evaluation_results.csv`)
- `--format`: Output format, either `csv` or `json` (default: `csv`)

## Question File Format

Questions should be in JSON format with the following structure:

```json
[
  {
    "id": 1,
    "category": "Precision",
    "question": "What is the UniProt ID for human BRCA1?",
    "expected_answer": "P38398",
    "notes": "Optional notes about this question"
  },
  {
    "id": 2,
    "category": "Completeness",
    "question": "How many genes are in GO term DNA repair?",
    "expected_answer": "Variable, check current database",
    "notes": "Tests comprehensive querying"
  }
]
```

### Required Fields

- `question`: The question text to evaluate

### Optional Fields

- `id`: Question identifier (defaults to index)
- `category`: One of: Precision, Completeness, Integration, Currency, Specificity, Structured Query
- `expected_answer`: The expected correct answer (for reference)
- `notes`: Additional notes about the question
- `mcp_servers`: Custom MCP server configurations (advanced)

### Question Categories

1. **Precision**: Require exact, verifiable data (IDs, sequences, properties)
2. **Completeness**: Require exhaustive data ("List all...", "How many...")
3. **Integration**: Require cross-database linking (ID conversions, mappings)
4. **Currency**: Benefit from up-to-date information
5. **Specificity**: Niche/specialized information (rare diseases, unusual compounds)
6. **Structured Query**: Complex database queries with filters

## Configuration File

You can customize the test runner behavior with a JSON config file:

```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 4000,
  "temperature": 1.0,
  "baseline_system_prompt": "Your custom baseline prompt...",
  "togomcp_system_prompt": "Your custom TogoMCP prompt...",
  "timeout": 60,
  "retry_attempts": 3,
  "retry_delay": 2
}
```

### Configuration Options

- `model`: Claude model to use (default: `claude-sonnet-4-20250514`)
- `max_tokens`: Maximum tokens in response (default: 4000)
- `temperature`: Sampling temperature (default: 1.0)
- `baseline_system_prompt`: System prompt for baseline tests
- `togomcp_system_prompt`: System prompt for TogoMCP tests
- `timeout`: Request timeout in seconds (default: 60)
- `retry_attempts`: Number of retry attempts on failure (default: 3)
- `retry_delay`: Delay between retries in seconds (default: 2)

## Output Format

### CSV Output (default)

The script generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| `question_id` | Question identifier |
| `date` | Evaluation date (YYYY-MM-DD) |
| `category` | Question category |
| `question_text` | The question asked |
| `baseline_success` | Whether baseline test succeeded (True/False) |
| `baseline_text` | Baseline answer text |
| `baseline_error` | Error message if baseline failed |
| `baseline_time` | Time taken for baseline test (seconds) |
| `baseline_input_tokens` | Input tokens used (baseline) |
| `baseline_output_tokens` | Output tokens used (baseline) |
| `togomcp_success` | Whether TogoMCP test succeeded (True/False) |
| `togomcp_text` | TogoMCP answer text |
| `togomcp_error` | Error message if TogoMCP failed |
| `togomcp_time` | Time taken for TogoMCP test (seconds) |
| `togomcp_input_tokens` | Input tokens used (TogoMCP) |
| `togomcp_output_tokens` | Output tokens used (TogoMCP) |
| `tools_used` | Comma-separated list of tools used |
| `tool_details` | JSON array of tool use details |
| `expected_answer` | Expected answer (from question file) |
| `notes` | Notes (from question file) |

### JSON Output

If you use `--format json`, the output will be a JSON array with the same fields as above.

## Features

### Automatic Retry

The test runner automatically retries failed API calls up to 3 times (configurable) with delays between attempts.

### Progress Tracking

During evaluation, you'll see real-time progress:

```
[1/10] Testing Q1: Precision
  Question: What is the UniProt ID for human BRCA1?
  ⏳ Running baseline test (no tools)...
  ✓ Baseline completed in 2.34s
  ⏳ Running TogoMCP test (with tools)...
  ✓ TogoMCP completed in 3.67s
    Tools used: search_uniprot_entity
```

### Intermediate Saves

Results are automatically saved every 5 questions to `evaluation_results_intermediate.csv` to prevent data loss during long runs.

### Interrupt Handling

You can safely interrupt the evaluation with Ctrl+C. Results collected so far will be preserved.

### Summary Statistics

After completion, you'll see a summary:

```
==============================================================
EVALUATION SUMMARY
==============================================================
Total questions:        10
Baseline success rate:  10/10 (100.0%)
TogoMCP success rate:   10/10 (100.0%)
Questions using tools:  8/10 (80.0%)
Avg baseline time:      2.15s
Avg TogoMCP time:       3.42s

Questions by category:
  Completeness: 2
  Integration: 3
  Precision: 5
==============================================================
```

## Example Workflow

### 1. Create Your Questions

```bash
# Copy the example and customize
cp example_questions.json my_questions.json
nano my_questions.json
```

### 2. Test with a Small Set First

```json
[
  {
    "id": 1,
    "category": "Precision",
    "question": "What is the UniProt ID for human TP53?",
    "expected_answer": "P04637"
  }
]
```

### 3. Run the Test

```bash
python automated_test_runner.py my_questions.json -o test_results.csv
```

### 4. Review Results

```bash
# View in a spreadsheet
open test_results.csv

# Or view in terminal
column -s, -t < test_results.csv | less -S
```

### 5. Analyze and Iterate

- Compare baseline vs TogoMCP answers
- Check which tools were used
- Verify expected answers
- Refine questions that didn't work well
- Add more questions to fill gaps

## Integration with Evaluation Framework

The CSV output is designed to be compatible with the evaluation tracker:

```bash
# You can import automated results into your evaluation tracker
# Then add manual scoring columns for the rubric dimensions
```

To add manual scoring to the automated results:

1. Open the CSV in a spreadsheet application
2. Add columns: `Accuracy`, `Precision`, `Completeness`, `Verifiability`, `Currency`, `Impossibility`
3. Score each dimension 0-3 based on the rubric
4. Add `Total_Score` and `Assessment` columns
5. Use the existing evaluation rubric for consistent scoring

## Troubleshooting

### API Key Not Set

```
Error: ANTHROPIC_API_KEY environment variable not set.
```

**Solution**: Export your API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Questions File Not Found

```
✗ Error: Questions file not found: questions.json
```

**Solution**: Check the file path and ensure the file exists.

### API Rate Limits

If you hit rate limits, you can:
- Reduce the number of questions
- Add delays between questions in the config
- Use a smaller model if appropriate

### Timeouts

If tests are timing out:
- Increase `timeout` in config.json
- Simplify complex questions
- Check your internet connection

## Advanced Usage

### Custom MCP Servers

You can specify custom MCP server configurations per question:

```json
{
  "id": 1,
  "question": "Your question here",
  "mcp_servers": [
    {
      "type": "url",
      "url": "https://custom-mcp-server.example.com/mcp",
      "name": "CustomMCP"
    }
  ]
}
```

### Batch Processing

For large evaluations, consider splitting into batches:

```bash
# Process 10 questions at a time
python automated_test_runner.py batch1.json -o results_batch1.csv
python automated_test_runner.py batch2.json -o results_batch2.csv
python automated_test_runner.py batch3.json -o results_batch3.csv

# Combine results
cat results_batch*.csv > combined_results.csv
```

### Programmatic Usage

You can also use the TestRunner class in your own Python scripts:

```python
from automated_test_runner import TestRunner

# Initialize
runner = TestRunner(config_path="config.json")

# Load questions
questions = runner.load_questions("questions.json")

# Run evaluations
results = runner.run_all_evaluations(questions)

# Export
runner.export_results("results.csv", format="csv")

# Access results programmatically
for result in results:
    print(f"Q{result['question_id']}: {result['tools_used']}")
```

## Tips for Success

1. **Start Small**: Test with 3-5 questions first
2. **Verify Answers**: Check expected answers against actual databases
3. **Document Everything**: Use the `notes` field liberally
4. **Monitor Costs**: Each question makes 2 API calls (baseline + TogoMCP)
5. **Save Frequently**: The script auto-saves, but you can manually save intermediate results
6. **Review Failures**: Check `*_error` columns for any failures
7. **Compare Times**: Look at `*_time` columns to understand performance

## Contributing

If you develop improvements to the test runner:

1. Test thoroughly with various question types
2. Update this README with new features
3. Add example configurations if introducing new options
4. Consider backward compatibility

## License

This evaluation tooling follows the same license as the main TogoMCP project.
