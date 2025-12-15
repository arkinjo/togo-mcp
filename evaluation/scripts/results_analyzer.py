#!/usr/bin/env python3
"""
TogoMCP Results Analyzer

Analyzes the CSV output from automated_test_runner.py and provides insights.
"""

import csv
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any
import sys


class ResultsAnalyzer:
    """Analyze evaluation results from automated test runner."""
    
    def __init__(self, results_path: str):
        """
        Initialize analyzer with results file.
        
        Args:
            results_path: Path to CSV results file
        """
        self.results_path = results_path
        self.results = []
        self.load_results()
    
    def load_results(self):
        """Load results from CSV file."""
        try:
            with open(self.results_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.results = list(reader)
            print(f"✓ Loaded {len(self.results)} evaluation results from {self.results_path}")
        except Exception as e:
            print(f"✗ Error loading results: {e}")
            sys.exit(1)
    
    def _to_bool(self, value: str) -> bool:
        """Convert string to boolean."""
        return value.lower() in ('true', '1', 'yes')
    
    def _to_float(self, value: str, default: float = 0.0) -> float:
        """Convert string to float with default."""
        try:
            return float(value) if value else default
        except ValueError:
            return default
    
    def _to_int(self, value: str, default: int = 0) -> int:
        """Convert string to int with default."""
        try:
            return int(value) if value else default
        except ValueError:
            return default
    
    def print_summary(self):
        """Print overall summary statistics."""
        total = len(self.results)
        if total == 0:
            print("No results to analyze")
            return
        
        # Success rates
        baseline_success = sum(1 for r in self.results if self._to_bool(r.get('baseline_success', 'False')))
        togomcp_success = sum(1 for r in self.results if self._to_bool(r.get('togomcp_success', 'False')))
        
        # Tool usage
        tools_used = sum(1 for r in self.results if r.get('tools_used', '').strip())
        
        # Timing
        baseline_times = [self._to_float(r.get('baseline_time', '0')) for r in self.results]
        togomcp_times = [self._to_float(r.get('togomcp_time', '0')) for r in self.results]
        avg_baseline_time = sum(baseline_times) / len(baseline_times) if baseline_times else 0
        avg_togomcp_time = sum(togomcp_times) / len(togomcp_times) if togomcp_times else 0
        
        # Token usage
        baseline_input = sum(self._to_int(r.get('baseline_input_tokens', '0')) for r in self.results)
        baseline_output = sum(self._to_int(r.get('baseline_output_tokens', '0')) for r in self.results)
        togomcp_input = sum(self._to_int(r.get('togomcp_input_tokens', '0')) for r in self.results)
        togomcp_output = sum(self._to_int(r.get('togomcp_output_tokens', '0')) for r in self.results)
        
        print("\n" + "="*70)
        print("EVALUATION RESULTS SUMMARY")
        print("="*70)
        
        print(f"\n📊 Overall Statistics:")
        print(f"  Total questions evaluated:     {total}")
        print(f"  Baseline success rate:         {baseline_success}/{total} ({baseline_success/total*100:.1f}%)")
        print(f"  TogoMCP success rate:          {togomcp_success}/{total} ({togomcp_success/total*100:.1f}%)")
        print(f"  Questions using tools:         {tools_used}/{total} ({tools_used/total*100:.1f}%)")
        
        print(f"\n⏱️  Response Times:")
        print(f"  Average baseline time:         {avg_baseline_time:.2f}s")
        print(f"  Average TogoMCP time:          {avg_togomcp_time:.2f}s")
        print(f"  Time difference:               {avg_togomcp_time - avg_baseline_time:+.2f}s")
        
        print(f"\n🔤 Token Usage:")
        print(f"  Baseline (input):              {baseline_input:,} tokens")
        print(f"  Baseline (output):             {baseline_output:,} tokens")
        print(f"  TogoMCP (input):               {togomcp_input:,} tokens")
        print(f"  TogoMCP (output):              {togomcp_output:,} tokens")
        print(f"  Total baseline tokens:         {baseline_input + baseline_output:,}")
        print(f"  Total TogoMCP tokens:          {togomcp_input + togomcp_output:,}")
    
    def analyze_by_category(self):
        """Analyze results broken down by category."""
        categories = defaultdict(lambda: {
            'total': 0,
            'baseline_success': 0,
            'togomcp_success': 0,
            'tools_used': 0,
            'baseline_time': [],
            'togomcp_time': []
        })
        
        for r in self.results:
            cat = r.get('category', 'Unknown')
            categories[cat]['total'] += 1
            
            if self._to_bool(r.get('baseline_success', 'False')):
                categories[cat]['baseline_success'] += 1
            
            if self._to_bool(r.get('togomcp_success', 'False')):
                categories[cat]['togomcp_success'] += 1
            
            if r.get('tools_used', '').strip():
                categories[cat]['tools_used'] += 1
            
            categories[cat]['baseline_time'].append(self._to_float(r.get('baseline_time', '0')))
            categories[cat]['togomcp_time'].append(self._to_float(r.get('togomcp_time', '0')))
        
        print("\n" + "="*70)
        print("ANALYSIS BY CATEGORY")
        print("="*70)
        
        for cat in sorted(categories.keys()):
            stats = categories[cat]
            total = stats['total']
            
            avg_base = sum(stats['baseline_time']) / len(stats['baseline_time']) if stats['baseline_time'] else 0
            avg_togo = sum(stats['togomcp_time']) / len(stats['togomcp_time']) if stats['togomcp_time'] else 0
            
            print(f"\n📁 {cat}:")
            print(f"  Questions:          {total}")
            print(f"  Baseline success:   {stats['baseline_success']}/{total} ({stats['baseline_success']/total*100:.1f}%)")
            print(f"  TogoMCP success:    {stats['togomcp_success']}/{total} ({stats['togomcp_success']/total*100:.1f}%)")
            print(f"  Used tools:         {stats['tools_used']}/{total} ({stats['tools_used']/total*100:.1f}%)")
            print(f"  Avg baseline time:  {avg_base:.2f}s")
            print(f"  Avg TogoMCP time:   {avg_togo:.2f}s")
    
    def analyze_tool_usage(self):
        """Analyze which tools were used most frequently."""
        tool_counts = defaultdict(int)
        tool_by_category = defaultdict(lambda: defaultdict(int))
        
        for r in self.results:
            tools = r.get('tools_used', '').strip()
            if not tools:
                continue
            
            category = r.get('category', 'Unknown')
            
            # Split comma-separated tool names
            for tool in tools.split(','):
                tool = tool.strip()
                if tool:
                    tool_counts[tool] += 1
                    tool_by_category[category][tool] += 1
        
        if not tool_counts:
            print("\n⚠ No tool usage found in results")
            return
        
        print("\n" + "="*70)
        print("TOOL USAGE ANALYSIS")
        print("="*70)
        
        print(f"\n🔧 Most Frequently Used Tools:")
        for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.results)) * 100
            print(f"  {tool:40} {count:3} uses ({percentage:.1f}% of questions)")
        
        print(f"\n📁 Tool Usage by Category:")
        for category in sorted(tool_by_category.keys()):
            print(f"\n  {category}:")
            for tool, count in sorted(tool_by_category[category].items(), key=lambda x: x[1], reverse=True):
                print(f"    {tool:38} {count:3} uses")
    
    def identify_failures(self):
        """Identify and report failures."""
        baseline_failures = []
        togomcp_failures = []
        
        for r in self.results:
            q_id = r.get('question_id', '?')
            
            if not self._to_bool(r.get('baseline_success', 'False')):
                baseline_failures.append({
                    'id': q_id,
                    'question': r.get('question_text', '')[:60] + '...',
                    'error': r.get('baseline_error', 'Unknown error')
                })
            
            if not self._to_bool(r.get('togomcp_success', 'False')):
                togomcp_failures.append({
                    'id': q_id,
                    'question': r.get('question_text', '')[:60] + '...',
                    'error': r.get('togomcp_error', 'Unknown error')
                })
        
        if baseline_failures or togomcp_failures:
            print("\n" + "="*70)
            print("FAILURES ANALYSIS")
            print("="*70)
        
        if baseline_failures:
            print(f"\n❌ Baseline Failures ({len(baseline_failures)}):")
            for f in baseline_failures:
                print(f"\n  Q{f['id']}: {f['question']}")
                print(f"    Error: {f['error']}")
        
        if togomcp_failures:
            print(f"\n❌ TogoMCP Failures ({len(togomcp_failures)}):")
            for f in togomcp_failures:
                print(f"\n  Q{f['id']}: {f['question']}")
                print(f"    Error: {f['error']}")
        
        if not baseline_failures and not togomcp_failures:
            print("\n✓ No failures detected - all tests completed successfully!")
    
    def compare_answers(self, verbose: bool = False):
        """Compare baseline vs TogoMCP answers."""
        print("\n" + "="*70)
        print("BASELINE vs TogoMCP COMPARISON")
        print("="*70)
        
        different_answers = 0
        used_tools = 0
        
        for r in self.results:
            baseline_text = r.get('baseline_text', '').strip()
            togomcp_text = r.get('togomcp_text', '').strip()
            tools = r.get('tools_used', '').strip()
            
            if tools:
                used_tools += 1
            
            # Simple comparison (could be enhanced)
            if baseline_text != togomcp_text:
                different_answers += 1
                
                if verbose:
                    q_id = r.get('question_id', '?')
                    question = r.get('question_text', '')[:60]
                    print(f"\nQ{q_id}: {question}...")
                    print(f"  Baseline: {baseline_text[:100]}...")
                    print(f"  TogoMCP:  {togomcp_text[:100]}...")
                    if tools:
                        print(f"  Tools:    {tools}")
        
        print(f"\n📊 Comparison Statistics:")
        print(f"  Questions with different answers:  {different_answers}/{len(self.results)} ({different_answers/len(self.results)*100:.1f}%)")
        print(f"  Questions using tools:             {used_tools}/{len(self.results)} ({used_tools/len(self.results)*100:.1f}%)")
    
    def export_insights(self, output_path: str):
        """Export analysis insights to JSON."""
        insights = {
            'total_questions': len(self.results),
            'summary': {},
            'by_category': {},
            'tool_usage': {},
            'failures': {
                'baseline': [],
                'togomcp': []
            }
        }
        
        # Calculate summary stats
        baseline_success = sum(1 for r in self.results if self._to_bool(r.get('baseline_success', 'False')))
        togomcp_success = sum(1 for r in self.results if self._to_bool(r.get('togomcp_success', 'False')))
        tools_used = sum(1 for r in self.results if r.get('tools_used', '').strip())
        
        insights['summary'] = {
            'baseline_success_rate': baseline_success / len(self.results) if self.results else 0,
            'togomcp_success_rate': togomcp_success / len(self.results) if self.results else 0,
            'tool_usage_rate': tools_used / len(self.results) if self.results else 0
        }
        
        # Export to JSON
        with open(output_path, 'w') as f:
            json.dump(insights, f, indent=2)
        
        print(f"\n✓ Insights exported to {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze TogoMCP evaluation results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  python results_analyzer.py evaluation_results.csv
  
  # Verbose comparison
  python results_analyzer.py evaluation_results.csv -v
  
  # Export insights to JSON
  python results_analyzer.py evaluation_results.csv -o insights.json
        """
    )
    
    parser.add_argument(
        "results_file",
        help="Path to CSV results file from automated_test_runner.py"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed comparisons"
    )
    parser.add_argument(
        "-o", "--output",
        help="Export insights to JSON file",
        default=None
    )
    
    args = parser.parse_args()
    
    # Verify results file exists
    if not Path(args.results_file).exists():
        print(f"✗ Error: Results file not found: {args.results_file}")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = ResultsAnalyzer(args.results_file)
    
    # Run analyses
    analyzer.print_summary()
    analyzer.analyze_by_category()
    analyzer.analyze_tool_usage()
    analyzer.identify_failures()
    analyzer.compare_answers(verbose=args.verbose)
    
    # Export insights if requested
    if args.output:
        analyzer.export_insights(args.output)
    
    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
