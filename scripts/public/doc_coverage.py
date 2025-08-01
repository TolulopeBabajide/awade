#!/usr/bin/env python3
"""
Awade Documentation Coverage Script

This script analyzes the documentation coverage of the Awade project, including Python files, API endpoints, markdown docs, and configuration files. It generates detailed reports and actionable recommendations to help maintain high-quality documentation across the codebase.

Usage:
    python scripts/doc_coverage.py --save

Author: Tolulope Babajide
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class DocCoverageItem:
    """Represents a documentation coverage item."""
    name: str
    path: str
    type: str  # 'file', 'function', 'class', 'module', 'api_endpoint'
    status: str  # 'documented', 'missing', 'outdated', 'placeholder'
    priority: str  # 'high', 'medium', 'low'
    description: str = ""
    last_updated: Optional[str] = None
    word_count: int = 0
    has_examples: bool = False
    has_code_samples: bool = False

@dataclass
class CoverageReport:
    """Represents a documentation coverage report."""
    timestamp: str
    total_items: int
    documented_items: int
    missing_items: int
    outdated_items: int
    placeholder_items: int
    coverage_percentage: float
    items: List[DocCoverageItem]
    categories: Dict[str, Dict[str, Any]]
    recommendations: List[str]

class DocumentationCoverageTracker:
    """Tracks documentation coverage across the Awade project."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.coverage_items = []
        self.ignore_patterns = [
            r'__pycache__',
            r'\.git',
            r'\.env',
            r'node_modules',
            r'\.pyc$',
            r'\.DS_Store',
            r'logs/',
            r'dist/',
            r'build/',
            r'venv/',
            r'\.venv/',
            r'env/',
            r'\.env/',
            r'cache/',
            r'\.pytest_cache/',
            r'\.mypy_cache/',
            r'\.coverage',
            r'htmlcov/',
            r'\.tox/',
            r'\.eggs/',
            r'\.idea/',
            r'\.vscode/',
            r'\.cursor/',
            r'\.DS_Store',
            r'Thumbs\.db',
            r'\.github/',
            r'contracts/',
            r'server\.log'
        ]
        
    def should_ignore(self, path: Path) -> bool:
        """
        Check if a path should be ignored during documentation analysis.

        Args:
            path (Path): The file or directory path to check.

        Returns:
            bool: True if the path matches any ignore pattern, False otherwise.
        """
        path_str = str(path)
        return any(re.search(pattern, path_str) for pattern in self.ignore_patterns)
    
    def analyze_python_files(self) -> List[DocCoverageItem]:
        """Analyze Python files for documentation coverage."""
        items = []
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if self.should_ignore(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                # Analyze file-level documentation
                file_doc = ast.get_docstring(tree)
                if file_doc:
                    items.append(DocCoverageItem(
                        name=py_file.name,
                        path=str(py_file.relative_to(self.project_root)),
                        type="file",
                        status="documented" if len(file_doc.strip()) > 50 else "placeholder",
                        priority="high" if "main" in py_file.name or "app" in py_file.name else "medium",
                        description=file_doc[:200] + "..." if len(file_doc) > 200 else file_doc,
                        word_count=len(file_doc.split()),
                        has_examples="example" in file_doc.lower() or "usage" in file_doc.lower(),
                        has_code_samples="```" in file_doc or "code" in file_doc.lower()
                    ))
                else:
                    items.append(DocCoverageItem(
                        name=py_file.name,
                        path=str(py_file.relative_to(self.project_root)),
                        type="file",
                        status="missing",
                        priority="high" if "main" in py_file.name or "app" in py_file.name else "medium",
                        description="No file-level documentation found"
                    ))
                
                # Analyze functions and classes
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        doc = ast.get_docstring(node)
                        if doc:
                            items.append(DocCoverageItem(
                                name=f"{node.name}",
                                path=f"{py_file.relative_to(self.project_root)}:{node.lineno}",
                                type="function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "class",
                                status="documented" if len(doc.strip()) > 20 else "placeholder",
                                priority="medium",
                                description=doc[:150] + "..." if len(doc) > 150 else doc,
                                word_count=len(doc.split()),
                                has_examples="example" in doc.lower(),
                                has_code_samples="```" in doc
                            ))
                        else:
                            items.append(DocCoverageItem(
                                name=f"{node.name}",
                                path=f"{py_file.relative_to(self.project_root)}:{node.lineno}",
                                type="function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "class",
                                status="missing",
                                priority="medium",
                                description="No documentation found"
                            ))
                            
            except Exception as e:
                items.append(DocCoverageItem(
                    name=py_file.name,
                    path=str(py_file.relative_to(self.project_root)),
                    type="file",
                    status="outdated",
                    priority="medium",
                    description=f"Error analyzing file: {e}"
                ))
        
        return items
    
    def analyze_api_endpoints(self) -> List[DocCoverageItem]:
        """Analyze API endpoints for documentation coverage."""
        items = []
        
        # Check for FastAPI app files
        api_files = list(self.project_root.rglob("main.py")) + list(self.project_root.rglob("app.py"))
        
        for api_file in api_files:
            if self.should_ignore(api_file):
                continue
                
            try:
                with open(api_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for FastAPI route decorators
                route_patterns = [
                    r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
                    r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
                ]
                
                for pattern in route_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        method, endpoint = match.groups()
                        items.append(DocCoverageItem(
                            name=f"{method.upper()} {endpoint}",
                            path=f"{api_file.relative_to(self.project_root)}:{match.start()}",
                            type="api_endpoint",
                            status="documented",  # Assume documented if found
                            priority="high",
                            description=f"API endpoint: {method.upper()} {endpoint}"
                        ))
                        
            except Exception as e:
                items.append(DocCoverageItem(
                    name=api_file.name,
                    path=str(api_file.relative_to(self.project_root)),
                    type="file",
                    status="outdated",
                    priority="high",
                    description=f"Error analyzing API file: {e}"
                ))
        
        return items
    
    def analyze_markdown_files(self) -> List[DocCoverageItem]:
        """Analyze markdown documentation files."""
        items = []
        md_files = list(self.project_root.rglob("*.md"))
        
        for md_file in md_files:
            if self.should_ignore(md_file):
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Analyze markdown content
                word_count = len(content.split())
                has_examples = "example" in content.lower() or "usage" in content.lower()
                has_code_samples = "```" in content
                has_placeholders = "under development" in content.lower() or "coming soon" in content.lower()
                
                # Determine status
                if has_placeholders:
                    status = "placeholder"
                elif word_count < 100:
                    status = "missing"
                elif word_count < 500:
                    status = "outdated"
                else:
                    status = "documented"
                
                items.append(DocCoverageItem(
                    name=md_file.name,
                    path=str(md_file.relative_to(self.project_root)),
                    type="documentation",
                    status=status,
                    priority="high" if "README" in md_file.name else "medium",
                    description=f"Documentation file with {word_count} words",
                    word_count=word_count,
                    has_examples=has_examples,
                    has_code_samples=has_code_samples
                ))
                
            except Exception as e:
                items.append(DocCoverageItem(
                    name=md_file.name,
                    path=str(md_file.relative_to(self.project_root)),
                    type="documentation",
                    status="outdated",
                    priority="medium",
                    description=f"Error analyzing markdown file: {e}"
                ))
        
        return items
    
    def analyze_config_files(self) -> List[DocCoverageItem]:
        """Analyze configuration files for documentation."""
        items = []
        config_files = [
            "requirements.txt",
            "package.json",
            "docker-compose.yml",
            "Dockerfile",
            ".env.example",
            ".cursor/mcp.json"
        ]
        
        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for comments/documentation
                    has_comments = "#" in content or "//" in content or "<!--" in content
                    
                    items.append(DocCoverageItem(
                        name=config_file,
                        path=config_file,
                        type="configuration",
                        status="documented" if has_comments else "missing",
                        priority="medium",
                        description=f"Configuration file: {config_file}",
                        word_count=len(content.split())
                    ))
                    
                except Exception as e:
                    items.append(DocCoverageItem(
                        name=config_file,
                        path=config_file,
                        type="configuration",
                        status="outdated",
                        priority="medium",
                        description=f"Error analyzing config file: {e}"
                    ))
        
        return items
    
    def generate_recommendations(self, items: List[DocCoverageItem]) -> List[str]:
        """Generate recommendations based on coverage analysis."""
        recommendations = []
        
        # Count items by status and priority
        status_counts = defaultdict(int)
        priority_counts = defaultdict(lambda: defaultdict(int))
        
        for item in items:
            status_counts[item.status] += 1
            priority_counts[item.priority][item.status] += 1
        
        # High priority missing items
        high_priority_missing = [item for item in items 
                               if item.status == "missing" and item.priority == "high"]
        if high_priority_missing:
            recommendations.append(
                f"🔴 {len(high_priority_missing)} high-priority items need documentation: "
                f"{', '.join(item.name for item in high_priority_missing[:5])}"
            )
        
        # Placeholder items
        placeholder_items = [item for item in items if item.status == "placeholder"]
        if placeholder_items:
            recommendations.append(
                f"🟡 {len(placeholder_items)} items have placeholder documentation that needs expansion"
            )
        
        # Outdated items
        outdated_items = [item for item in items if item.status == "outdated"]
        if outdated_items:
            recommendations.append(
                f"🟠 {len(outdated_items)} items have outdated documentation that needs updating"
            )
        
        # Coverage percentage
        documented = status_counts.get("documented", 0)
        total = len(items)
        coverage = (documented / total * 100) if total > 0 else 0
        
        if coverage < 80:
            recommendations.append(
                f"📊 Overall documentation coverage is {coverage:.1f}% - aim for 80%+"
            )
        
        # Missing examples
        items_without_examples = [item for item in items 
                                if item.status == "documented" and not item.has_examples]
        if items_without_examples:
            recommendations.append(
                f"💡 {len(items_without_examples)} documented items could benefit from examples"
            )
        
        return recommendations
    
    def categorize_items(self, items: List[DocCoverageItem]) -> Dict[str, Dict[str, Any]]:
        """Categorize items by type and status."""
        categories = defaultdict(lambda: {
            "total": 0,
            "documented": 0,
            "missing": 0,
            "outdated": 0,
            "placeholder": 0,
            "coverage_percentage": 0.0
        })
        
        for item in items:
            categories[item.type]["total"] += 1
            categories[item.type][item.status] += 1
        
        # Calculate coverage percentages
        for category in categories:
            total = categories[category]["total"]
            documented = categories[category]["documented"]
            categories[category]["coverage_percentage"] = (
                (documented / total * 100) if total > 0 else 0
            )
        
        return dict(categories)
    
    def run_analysis(self) -> CoverageReport:
        """Run complete documentation coverage analysis."""
        print("🔍 Starting documentation coverage analysis...")
        
        # Analyze different types of files
        python_items = self.analyze_python_files()
        api_items = self.analyze_api_endpoints()
        markdown_items = self.analyze_markdown_files()
        config_items = self.analyze_config_files()
        
        # Combine all items
        all_items = python_items + api_items + markdown_items + config_items
        
        # Calculate overall statistics
        total_items = len(all_items)
        documented_items = len([item for item in all_items if item.status == "documented"])
        missing_items = len([item for item in all_items if item.status == "missing"])
        outdated_items = len([item for item in all_items if item.status == "outdated"])
        placeholder_items = len([item for item in all_items if item.status == "placeholder"])
        
        coverage_percentage = (documented_items / total_items * 100) if total_items > 0 else 0
        
        # Generate recommendations
        recommendations = self.generate_recommendations(all_items)
        
        # Categorize items
        categories = self.categorize_items(all_items)
        
        report = CoverageReport(
            timestamp=datetime.now().isoformat(),
            total_items=total_items,
            documented_items=documented_items,
            missing_items=missing_items,
            outdated_items=outdated_items,
            placeholder_items=placeholder_items,
            coverage_percentage=coverage_percentage,
            items=all_items,
            categories=categories,
            recommendations=recommendations
        )
        
        return report
    
    def print_summary(self, report: CoverageReport) -> None:
        """Print coverage summary to console."""
        print("\n" + "="*60)
        print("📊 DOCUMENTATION COVERAGE SUMMARY")
        print("="*60)
        print(f"Total Items: {report.total_items}")
        print(f"✅ Documented: {report.documented_items}")
        print(f"❌ Missing: {report.missing_items}")
        print(f"🟠 Outdated: {report.outdated_items}")
        print(f"🟡 Placeholder: {report.placeholder_items}")
        print(f"📈 Coverage: {report.coverage_percentage:.1f}%")
        print("="*60)
        
        print("\n📋 BY CATEGORY:")
        for category, stats in report.categories.items():
            print(f"  {category.title()}: {stats['coverage_percentage']:.1f}% "
                  f"({stats['documented']}/{stats['total']})")
        
        if report.recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for rec in report.recommendations:
                print(f"  • {rec}")
        
        print("="*60)
    
    def print_missing_items(self, report: CoverageReport) -> None:
        """Print detailed list of missing documentation items."""
        missing_items = [item for item in report.items if item.status == "missing"]
        
        if not missing_items:
            print("✅ No missing documentation items found!")
            return
        
        print(f"\n❌ MISSING DOCUMENTATION ITEMS ({len(missing_items)} items):")
        print("="*60)
        
        # Group by type
        by_type = {}
        for item in missing_items:
            if item.type not in by_type:
                by_type[item.type] = []
            by_type[item.type].append(item)
        
        for item_type, items in by_type.items():
            print(f"\n📁 {item_type.upper()} ({len(items)} items):")
            for item in sorted(items, key=lambda x: x.path):
                priority_icon = "🔴" if item.priority == "high" else "🟡" if item.priority == "medium" else "🟢"
                print(f"  {priority_icon} {item.path} - {item.name}")
        
        print("="*60)
    
    def save_report(self, report: CoverageReport, output_path: str = "logs/doc_coverage_report.json") -> None:
        """Save coverage report to file."""
        # Create logs directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Convert dataclasses to dictionaries
        report_dict = asdict(report)
        
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        print(f"📊 Coverage report saved to {output_path}")

def main():
    """Main function for documentation coverage tracking."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Track documentation coverage for Awade")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output", default="logs/doc_coverage_report.json", 
                       help="Output path for coverage report")
    parser.add_argument("--save", action="store_true", help="Save detailed report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--show-missing", action="store_true", help="Show detailed list of missing items")
    
    args = parser.parse_args()
    
    print("📚 Starting Awade Documentation Coverage Analysis...")
    
    # Initialize tracker
    tracker = DocumentationCoverageTracker(args.project_root)
    
    # Run analysis
    report = tracker.run_analysis()
    
    # Print summary
    tracker.print_summary(report)
    
    # Show missing items if requested
    if args.show_missing:
        tracker.print_missing_items(report)
    
    # Save report if requested
    if args.save:
        tracker.save_report(report, args.output)
    
    # Exit with appropriate code
    if report.coverage_percentage < 70:
        print(f"\n⚠️  Documentation coverage is below 70% ({report.coverage_percentage:.1f}%)")
        sys.exit(1)
    else:
        print(f"\n✅ Documentation coverage is good ({report.coverage_percentage:.1f}%)")
        sys.exit(0)

if __name__ == "__main__":
    main() 