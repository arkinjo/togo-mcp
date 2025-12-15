#!/usr/bin/env python3
"""
Cleanup script to organize agent_scripts directory.
Moves debug/test files to archive folder.
"""

import os
import shutil
from pathlib import Path

# Get script directory
script_dir = Path(__file__).parent

# Create archive directories
debug_dir = script_dir / "_archive_debug"
docs_dir = script_dir / "_archive_docs"
debug_dir.mkdir(exist_ok=True)
docs_dir.mkdir(exist_ok=True)

print("Cleaning up agent_scripts directory...")
print("="*60)

# Files to move to debug archive
debug_patterns = [
    "test_*.py",
    "test_*.txt", 
    "check_*.py",
    "check_*.txt",
    "debug_*.py",
    "debug_*.txt",
    "verify_*.py"
]

# Specific files to archive
debug_files = [
    "automated_test_runner_api.py",
    "automated_test_runner_backup.py",
    "evaluation_results_intermediate.csv",
    "test_api_results.csv"
]

# Move old/renamed results
if (script_dir / "evaluation_results.csv").exists():
    old_results = script_dir / "evaluation_results.csv"
    new_path = debug_dir / "evaluation_results_OLD.csv"
    shutil.move(str(old_results), str(new_path))
    print(f"✓ Moved evaluation_results.csv → _archive_debug/evaluation_results_OLD.csv")

# Rename FIXED version to main
if (script_dir / "evaluation_results_FIXED.csv").exists():
    shutil.move(
        str(script_dir / "evaluation_results_FIXED.csv"),
        str(script_dir / "evaluation_results.csv")
    )
    print(f"✓ Renamed evaluation_results_FIXED.csv → evaluation_results.csv")

# Move debug files
moved_count = 0
for pattern in debug_patterns:
    for file in script_dir.glob(pattern):
        if file.is_file():
            dest = debug_dir / file.name
            shutil.move(str(file), str(dest))
            moved_count += 1
            print(f"✓ Moved {file.name} → _archive_debug/")

for filename in debug_files:
    file = script_dir / filename
    if file.exists():
        dest = debug_dir / filename
        shutil.move(str(file), str(dest))
        moved_count += 1
        print(f"✓ Moved {filename} → _archive_debug/")

# Move old docs
doc_files = [
    "CORRECTION_SUMMARY.md",
    "FIX_EMPTY_TEXT.md", 
    "FILES.md"
]

for filename in doc_files:
    file = script_dir / filename
    if file.exists():
        dest = docs_dir / filename
        shutil.move(str(file), str(dest))
        print(f"✓ Moved {filename} → _archive_docs/")

print("\n" + "="*60)
print(f"Cleanup complete! Moved {moved_count} debug files")
print("\nCurrent directory structure:")
print("  Main files:")
for file in sorted(script_dir.glob("*.py")):
    print(f"    {file.name}")
for file in sorted(script_dir.glob("*.json")):
    print(f"    {file.name}")
for file in sorted(script_dir.glob("*.csv")):
    print(f"    {file.name}")
    
print("\n  Documentation:")
for file in sorted(script_dir.glob("*.md")):
    print(f"    {file.name}")

print("\n  Archives:")
print(f"    _archive_debug/ ({len(list(debug_dir.glob('*')))} files)")
print(f"    _archive_docs/ ({len(list(docs_dir.glob('*')))} files)")

print("\n✅ Done! Your directory is now clean and organized.")
