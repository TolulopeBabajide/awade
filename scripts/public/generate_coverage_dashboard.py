#!/usr/bin/env python3
"""
Generate HTML Dashboard for Documentation Coverage
Creates an interactive HTML dashboard to visualize coverage data.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def load_coverage_report(report_path: str = "logs/doc_coverage_report.json") -> Dict[str, Any]:
    """Load coverage report from JSON file."""
    try:
        with open(report_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Coverage report not found: {report_path}")
        print("Run 'python scripts/doc_coverage.py --save' first")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in coverage report: {report_path}")
        sys.exit(1)

def generate_html_dashboard(report: Dict[str, Any], output_path: str = "logs/coverage_dashboard.html") -> None:
    """Generate HTML dashboard from coverage report."""
    
    # Calculate additional metrics
    categories = report.get('categories', {})
    items = report.get('items', [])
    
    # Status counts
    status_counts = {}
    for item in items:
        status = item.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Priority counts
    priority_counts = {}
    for item in items:
        priority = item.get('priority', 'unknown')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Awade Documentation Coverage Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            text-align: center;
            border-left: 4px solid #007bff;
            transition: transform 0.2s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .metric-label {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .coverage-high {{ color: #28a745; }}
        .coverage-medium {{ color: #ffc107; }}
        .coverage-low {{ color: #dc3545; }}
        
        .charts-section {{
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        .chart-title {{
            font-size: 1.3em;
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .details-section {{
            padding: 30px;
        }}
        
        .details-title {{
            font-size: 1.5em;
            color: #2c3e50;
            margin-bottom: 20px;
        }}
        
        .item-list {{
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #e9ecef;
            border-radius: 8px;
        }}
        
        .item {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .item:last-child {{
            border-bottom: none;
        }}
        
        .item-info {{
            flex: 1;
        }}
        
        .item-name {{
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .item-path {{
            font-size: 0.9em;
            color: #6c757d;
            margin-top: 5px;
        }}
        
        .item-status {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .status-documented {{ background: #d4edda; color: #155724; }}
        .status-missing {{ background: #f8d7da; color: #721c24; }}
        .status-outdated {{ background: #fff3cd; color: #856404; }}
        .status-placeholder {{ background: #d1ecf1; color: #0c5460; }}
        
        .recommendations {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .recommendations h3 {{
            color: #1976d2;
            margin-bottom: 15px;
        }}
        
        .recommendations ul {{
            list-style: none;
        }}
        
        .recommendations li {{
            margin-bottom: 8px;
            padding-left: 20px;
            position: relative;
        }}
        
        .recommendations li:before {{
            content: "💡";
            position: absolute;
            left: 0;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Documentation Coverage</h1>
            <div class="subtitle">Awade Project • Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value coverage-{'high' if report['coverage_percentage'] >= 80 else 'medium' if report['coverage_percentage'] >= 70 else 'low'}">
                    {report['coverage_percentage']:.1f}%
                </div>
                <div class="metric-label">Overall Coverage</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value">{report['total_items']}</div>
                <div class="metric-label">Total Items</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value coverage-high">{report['documented_items']}</div>
                <div class="metric-label">Documented</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value coverage-low">{report['missing_items']}</div>
                <div class="metric-label">Missing</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value coverage-medium">{report['outdated_items']}</div>
                <div class="metric-label">Outdated</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-value coverage-medium">{report['placeholder_items']}</div>
                <div class="metric-label">Placeholder</div>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <div class="chart-title">Coverage by Category</div>
                <canvas id="categoryChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Status Distribution</div>
                <canvas id="statusChart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <div class="details-section">
            <div class="details-title">📋 Coverage by Category</div>
            <div class="item-list">
"""
    
    # Add category details
    for category, stats in categories.items():
        coverage_class = 'high' if stats['coverage_percentage'] >= 80 else 'medium' if stats['coverage_percentage'] >= 70 else 'low'
        html_content += f"""
                <div class="item">
                    <div class="item-info">
                        <div class="item-name">{category.title()}</div>
                        <div class="item-path">{stats['documented']}/{stats['total']} items documented</div>
                    </div>
                    <div class="item-status coverage-{coverage_class}">
                        {stats['coverage_percentage']:.1f}%
                    </div>
                </div>
"""
    
    html_content += """
            </div>
        </div>
        
        <div class="details-section">
            <div class="details-title">🔍 High Priority Missing Items</div>
            <div class="item-list">
"""
    
    # Add high priority missing items
    high_priority_missing = [item for item in items if item.get('status') == 'missing' and item.get('priority') == 'high']
    for item in high_priority_missing[:10]:  # Show top 10
        html_content += f"""
                <div class="item">
                    <div class="item-info">
                        <div class="item-name">{item['name']}</div>
                        <div class="item-path">{item['path']}</div>
                    </div>
                    <div class="item-status status-missing">Missing</div>
                </div>
"""
    
    if not high_priority_missing:
        html_content += """
                <div class="item">
                    <div class="item-info">
                        <div class="item-name">No high priority missing items</div>
                        <div class="item-path">Great job! 🎉</div>
                    </div>
                </div>
"""
    
    html_content += """
            </div>
        </div>
"""
    
    # Add recommendations if available
    if report.get('recommendations'):
        html_content += """
        <div class="details-section">
            <div class="recommendations">
                <h3>💡 Recommendations</h3>
                <ul>
"""
        for rec in report['recommendations']:
            html_content += f"""
                    <li>{rec}</li>
"""
        html_content += """
                </ul>
            </div>
        </div>
"""
    
    # Add JavaScript for charts
    html_content += f"""
        <div class="footer">
            Generated by Awade Documentation Coverage Tracker • 
            <a href="https://github.com/your-username/awade" style="color: #fff;">View on GitHub</a>
        </div>
    </div>
    
    <script>
        // Category Chart
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {{
            type: 'bar',
            data: {{
                labels: {list(categories.keys())},
                datasets: [{{
                    label: 'Coverage %',
                    data: {[stats['coverage_percentage'] for stats in categories.values()]},
                    backgroundColor: [
                        '#28a745',
                        '#17a2b8', 
                        '#ffc107',
                        '#dc3545',
                        '#6f42c1',
                        '#fd7e14'
                    ],
                    borderColor: [
                        '#1e7e34',
                        '#138496',
                        '#e0a800', 
                        '#c82333',
                        '#5a32a3',
                        '#e8590c'
                    ],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
        
        // Status Chart
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        new Chart(statusCtx, {{
            type: 'doughnut',
            data: {{
                labels: {list(status_counts.keys())},
                datasets: [{{
                    data: {list(status_counts.values())},
                    backgroundColor: [
                        '#28a745',
                        '#dc3545',
                        '#ffc107', 
                        '#17a2b8'
                    ],
                    borderWidth: 3,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Save HTML file
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"📊 HTML dashboard generated: {output_path}")

def main():
    """Main function for generating coverage dashboard."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate HTML dashboard for documentation coverage")
    parser.add_argument("--report", default="logs/doc_coverage_report.json", 
                       help="Path to coverage report JSON file")
    parser.add_argument("--output", default="logs/coverage_dashboard.html",
                       help="Output path for HTML dashboard")
    
    args = parser.parse_args()
    
    print("📊 Generating documentation coverage dashboard...")
    
    # Load coverage report
    report = load_coverage_report(args.report)
    
    # Generate HTML dashboard
    generate_html_dashboard(report, args.output)
    
    print("✅ Dashboard generation complete!")
    print(f"🌐 Open {args.output} in your browser to view the dashboard")

if __name__ == "__main__":
    main() 