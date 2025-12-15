#!/usr/bin/env python3
"""
TogoMCP Automated Test Runner

This script automates the evaluation of TogoMCP by running questions against:
1. Baseline (Claude without tools)
2. TogoMCP-enhanced (Claude with MCP tools)

It captures responses, timing, tool usage, and exports results to CSV.
"""

import json
import csv
import time
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import argparse
import sys

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed. Install with: pip install anthropic")
    sys.exit(1)


class TestRunner:
    """Manages automated evaluation of TogoMCP questions."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the test runner.
        
        Args:
            config_path: Path to configuration file (JSON)
        """
        self.config = self._load_config(config_path)
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Please set it with your API key."
            )
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.results = []
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults."""
        default_config = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4000,
            "temperature": 1.0,
            "baseline_system_prompt": (
                "Answer using only your training knowledge. "
                "Do not use any database tools or external resources. "
                "If you don't know something with certainty, say so."
            ),
            "togomcp_system_prompt": (
                "You have access to biological databases through MCP tools. "
                "Use them when they would improve the accuracy or completeness of your answer."
            ),
            "timeout": 60,  # seconds
            "retry_attempts": 3,
            "retry_delay": 2,  # seconds
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def load_questions(self, questions_path: str) -> List[Dict]:
        """
        Load questions from JSON file.
        
        Args:
            questions_path: Path to questions file
            
        Returns:
            List of question dictionaries
        """
        with open(questions_path, 'r') as f:
            questions = json.load(f)
        
        print(f"✓ Loaded {len(questions)} questions from {questions_path}")
        return questions
    
    def _make_api_call(
        self, 
        question: str, 
        system_prompt: str,
        use_tools: bool = False,
        mcp_servers: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Make a single API call to Claude.
        
        Args:
            question: The question to ask
            system_prompt: System prompt to use
            use_tools: Whether to enable tool use
            mcp_servers: MCP server configurations if use_tools=True
            
        Returns:
            Dictionary with response data
        """
        start_time = time.time()
        
        kwargs = {
            "model": self.config["model"],
            "max_tokens": self.config["max_tokens"],
            "temperature": self.config["temperature"],
            "system": system_prompt,
            "messages": [{"role": "user", "content": question}]
        }
        
        # Add MCP servers if tools are enabled
        if use_tools and mcp_servers:
            kwargs["mcp_servers"] = mcp_servers
        
        try:
            response = self.client.messages.create(**kwargs)
            elapsed_time = time.time() - start_time
            
            # Extract text content
            text_content = []
            tool_uses = []
            
            for block in response.content:
                if block.type == "text":
                    text_content.append(block.text)
                elif block.type == "tool_use":
                    tool_uses.append({
                        "name": block.name,
                        "input": block.input
                    })
            
            return {
                "success": True,
                "text": "\n".join(text_content),
                "tool_uses": tool_uses,
                "elapsed_time": elapsed_time,
                "stop_reason": response.stop_reason,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "elapsed_time": elapsed_time
            }
    
    def _run_with_retry(self, *args, **kwargs) -> Dict:
        """Run API call with retry logic."""
        for attempt in range(self.config["retry_attempts"]):
            result = self._make_api_call(*args, **kwargs)
            
            if result["success"]:
                return result
            
            if attempt < self.config["retry_attempts"] - 1:
                print(f"  ⚠ Attempt {attempt + 1} failed, retrying in {self.config['retry_delay']}s...")
                time.sleep(self.config["retry_delay"])
        
        return result
    
    def run_baseline_test(self, question_text: str) -> Dict:
        """
        Run baseline test (no tools).
        
        Args:
            question_text: The question to ask
            
        Returns:
            Dictionary with test results
        """
        return self._run_with_retry(
            question=question_text,
            system_prompt=self.config["baseline_system_prompt"],
            use_tools=False
        )
    
    def run_togomcp_test(
        self, 
        question_text: str,
        mcp_servers: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Run TogoMCP-enhanced test (with tools).
        
        Args:
            question_text: The question to ask
            mcp_servers: MCP server configurations
            
        Returns:
            Dictionary with test results
        """
        # Default MCP servers for TogoMCP
        if mcp_servers is None:
            mcp_servers = [
                {
                    "type": "url",
                    "url": "https://togomcp.rdfportal.org/mcp",
                    "name": "TogoMCP"
                }
            ]
        
        return self._run_with_retry(
            question=question_text,
            system_prompt=self.config["togomcp_system_prompt"],
            use_tools=True,
            mcp_servers=mcp_servers
        )
    
    def run_single_evaluation(self, question: Dict, index: int, total: int) -> Dict:
        """
        Run complete evaluation for a single question.
        
        Args:
            question: Question dictionary
            index: Current question index
            total: Total number of questions
            
        Returns:
            Dictionary with evaluation results
        """
        q_id = question.get("id", index)
        q_text = question["question"]
        category = question.get("category", "Unknown")
        
        print(f"\n[{index + 1}/{total}] Testing Q{q_id}: {category}")
        print(f"  Question: {q_text[:80]}{'...' if len(q_text) > 80 else ''}")
        
        # Run baseline test
        print("  ⏳ Running baseline test (no tools)...")
        baseline_result = self.run_baseline_test(q_text)
        
        if baseline_result["success"]:
            print(f"  ✓ Baseline completed in {baseline_result['elapsed_time']:.2f}s")
        else:
            print(f"  ✗ Baseline failed: {baseline_result['error']}")
        
        # Run TogoMCP test
        print("  ⏳ Running TogoMCP test (with tools)...")
        togomcp_result = self.run_togomcp_test(
            q_text,
            mcp_servers=question.get("mcp_servers")
        )
        
        if togomcp_result["success"]:
            tool_names = [t["name"] for t in togomcp_result["tool_uses"]]
            print(f"  ✓ TogoMCP completed in {togomcp_result['elapsed_time']:.2f}s")
            if tool_names:
                print(f"    Tools used: {', '.join(tool_names)}")
        else:
            print(f"  ✗ TogoMCP failed: {togomcp_result['error']}")
        
        # Compile results
        result = {
            "question_id": q_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "category": category,
            "question_text": q_text,
            "baseline_success": baseline_result["success"],
            "baseline_text": baseline_result.get("text", ""),
            "baseline_error": baseline_result.get("error", ""),
            "baseline_time": baseline_result["elapsed_time"],
            "togomcp_success": togomcp_result["success"],
            "togomcp_text": togomcp_result.get("text", ""),
            "togomcp_error": togomcp_result.get("error", ""),
            "togomcp_time": togomcp_result["elapsed_time"],
            "tools_used": ", ".join([t["name"] for t in togomcp_result.get("tool_uses", [])]),
            "tool_details": json.dumps(togomcp_result.get("tool_uses", [])),
            "expected_answer": question.get("expected_answer", ""),
            "notes": question.get("notes", "")
        }
        
        # Add token usage if available
        if baseline_result["success"]:
            result["baseline_input_tokens"] = baseline_result["usage"]["input_tokens"]
            result["baseline_output_tokens"] = baseline_result["usage"]["output_tokens"]
        
        if togomcp_result["success"]:
            result["togomcp_input_tokens"] = togomcp_result["usage"]["input_tokens"]
            result["togomcp_output_tokens"] = togomcp_result["usage"]["output_tokens"]
        
        return result
    
    def run_all_evaluations(self, questions: List[Dict]) -> List[Dict]:
        """
        Run evaluations for all questions.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            List of result dictionaries
        """
        total = len(questions)
        print(f"\n{'='*60}")
        print(f"Starting automated evaluation of {total} questions")
        print(f"{'='*60}")
        
        results = []
        
        for i, question in enumerate(questions):
            try:
                result = self.run_single_evaluation(question, i, total)
                results.append(result)
                
                # Save intermediate results every 5 questions
                if (i + 1) % 5 == 0:
                    self._save_intermediate_results(results, i + 1)
                    
            except KeyboardInterrupt:
                print("\n\n⚠ Evaluation interrupted by user")
                print(f"Completed {i} out of {total} questions")
                break
            except Exception as e:
                print(f"\n✗ Unexpected error: {e}")
                continue
        
        print(f"\n{'='*60}")
        print(f"Evaluation complete: {len(results)}/{total} questions processed")
        print(f"{'='*60}\n")
        
        self.results = results
        return results
    
    def _save_intermediate_results(self, results: List[Dict], count: int):
        """Save intermediate results during long runs."""
        intermediate_path = Path("evaluation_results_intermediate.csv")
        self._export_to_csv(results, str(intermediate_path))
        print(f"  💾 Saved intermediate results ({count} questions) to {intermediate_path}")
    
    def _export_to_csv(self, results: List[Dict], output_path: str):
        """Export results to CSV file."""
        if not results:
            print("⚠ No results to export")
            return
        
        fieldnames = [
            "question_id", "date", "category", "question_text",
            "baseline_success", "baseline_text", "baseline_error", "baseline_time",
            "baseline_input_tokens", "baseline_output_tokens",
            "togomcp_success", "togomcp_text", "togomcp_error", "togomcp_time",
            "togomcp_input_tokens", "togomcp_output_tokens",
            "tools_used", "tool_details", "expected_answer", "notes"
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    
    def export_results(self, output_path: str, format: str = "csv"):
        """
        Export evaluation results.
        
        Args:
            output_path: Path to save results
            format: Output format ('csv' or 'json')
        """
        if not self.results:
            print("⚠ No results to export")
            return
        
        if format == "csv":
            self._export_to_csv(self.results, output_path)
            print(f"✓ Results exported to {output_path} ({len(self.results)} questions)")
        elif format == "json":
            with open(output_path, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"✓ Results exported to {output_path} ({len(self.results)} questions)")
        else:
            print(f"✗ Unsupported format: {format}")
    
    def print_summary(self):
        """Print summary statistics."""
        if not self.results:
            print("No results to summarize")
            return
        
        total = len(self.results)
        baseline_success = sum(1 for r in self.results if r["baseline_success"])
        togomcp_success = sum(1 for r in self.results if r["togomcp_success"])
        
        avg_baseline_time = sum(r["baseline_time"] for r in self.results) / total
        avg_togomcp_time = sum(r["togomcp_time"] for r in self.results) / total
        
        tools_used_count = sum(1 for r in self.results if r["tools_used"])
        
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"Total questions:        {total}")
        print(f"Baseline success rate:  {baseline_success}/{total} ({baseline_success/total*100:.1f}%)")
        print(f"TogoMCP success rate:   {togomcp_success}/{total} ({togomcp_success/total*100:.1f}%)")
        print(f"Questions using tools:  {tools_used_count}/{total} ({tools_used_count/total*100:.1f}%)")
        print(f"Avg baseline time:      {avg_baseline_time:.2f}s")
        print(f"Avg TogoMCP time:       {avg_togomcp_time:.2f}s")
        
        # Category breakdown
        categories = {}
        for r in self.results:
            cat = r["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        print("\nQuestions by category:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")
        
        print("="*60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated TogoMCP Evaluation Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default config
  python automated_test_runner.py questions.json
  
  # Use custom config
  python automated_test_runner.py questions.json -c config.json
  
  # Specify output path
  python automated_test_runner.py questions.json -o results.csv
  
  # Export as JSON
  python automated_test_runner.py questions.json -o results.json --format json
        """
    )
    
    parser.add_argument(
        "questions_file",
        help="Path to questions JSON file"
    )
    parser.add_argument(
        "-c", "--config",
        help="Path to configuration JSON file",
        default=None
    )
    parser.add_argument(
        "-o", "--output",
        help="Output path for results (default: evaluation_results.csv)",
        default="evaluation_results.csv"
    )
    parser.add_argument(
        "--format",
        help="Output format: csv or json (default: csv)",
        choices=["csv", "json"],
        default="csv"
    )
    
    args = parser.parse_args()
    
    # Verify questions file exists
    if not Path(args.questions_file).exists():
        print(f"✗ Error: Questions file not found: {args.questions_file}")
        sys.exit(1)
    
    # Initialize test runner
    try:
        runner = TestRunner(config_path=args.config)
    except Exception as e:
        print(f"✗ Error initializing test runner: {e}")
        sys.exit(1)
    
    # Load questions
    try:
        questions = runner.load_questions(args.questions_file)
    except Exception as e:
        print(f"✗ Error loading questions: {e}")
        sys.exit(1)
    
    # Run evaluations
    runner.run_all_evaluations(questions)
    
    # Export results
    runner.export_results(args.output, format=args.format)
    
    # Print summary
    runner.print_summary()


if __name__ == "__main__":
    main()
