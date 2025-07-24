#!/usr/bin/env python3
"""
Awade Monitoring Dashboard
Provides real-time insights into project health, documentation status, and MCP server status.
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import requests
from collections import defaultdict

class AwadeMonitor:
    def __init__(self):
        """
        Initialize the AwadeMonitor.

        Sets up paths for project root, logs, documentation, backend, and frontend directories.
        """
        self.project_root = Path.cwd()
        self.logs_dir = self.project_root / "logs"
        self.docs_dir = self.project_root / "docs"
        self.backend_dir = self.project_root / "apps" / "backend"
        self.frontend_dir = self.project_root / "apps" / "frontend"
        
    def get_git_stats(self):
        """Get Git repository statistics."""
        try:
            # Get commit count
            commit_count = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            
            # Get last commit info
            last_commit = subprocess.run(
                ['git', 'log', '-1', '--format=%H|%an|%ad|%s'],
                capture_output=True, text=True, check=True
            ).stdout.strip().split('|')
            
            # Get branch info
            current_branch = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            
            # Get file count
            file_count = subprocess.run(
                ['git', 'ls-files'],
                capture_output=True, text=True, check=True
            ).stdout.strip().split('\n')
            
            return {
                'total_commits': int(commit_count),
                'last_commit': {
                    'hash': last_commit[0][:8],
                    'author': last_commit[1],
                    'date': last_commit[2],
                    'message': last_commit[3]
                },
                'current_branch': current_branch,
                'total_files': len([f for f in file_count if f]),
                'python_files': len([f for f in file_count if f.endswith('.py')]),
                'markdown_files': len([f for f in file_count if f.endswith('.md')])
            }
        except subprocess.CalledProcessError:
            return {'error': 'Git repository not found'}
    
    def get_documentation_status(self):
        """Check documentation completeness and health."""
        required_files = [
            'README.md',
            'docs/internal/api-contracts.md',
            'docs/internal/requirements.md',
            'docs/api/README.md',
            'AI_USE_POLICY.md',
            'LICENSE.md'
        ]
        
        status = {
            'total_required': len(required_files),
            'present': 0,
            'missing': [],
            'recent_updates': []
        }
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                status['present'] += 1
                
                # Check last modified date
                mtime = datetime.fromtimestamp(full_path.stat().st_mtime)
                if mtime > datetime.now() - timedelta(days=7):
                    status['recent_updates'].append({
                        'file': file_path,
                        'modified': mtime.strftime('%Y-%m-%d %H:%M')
                    })
            else:
                status['missing'].append(file_path)
        
        status['completeness'] = (status['present'] / status['total_required']) * 100
        return status
    
    def get_mcp_health(self):
        """Get MCP server health status."""
        mcp_file = self.project_root / '.cursor' / 'mcp.json'
        
        if not mcp_file.exists():
            return {'error': 'MCP configuration not found'}
        
        try:
            with open(mcp_file, 'r') as f:
                config = json.load(f)
            
            servers = config.get('mcpServers', {})
            
            health_data = {
                'total_servers': len(servers),
                'server_types': defaultdict(int),
                'documentation_servers': 0,
                'api_servers': 0
            }
            
            for name, server_config in servers.items():
                command = server_config.get('command', '')
                health_data['server_types'][command] += 1
                
                if any(keyword in name.lower() for keyword in ['doc', 'api', 'readme']):
                    health_data['documentation_servers'] += 1
                
                if 'openapi' in name.lower() or 'fastapi' in command.lower():
                    health_data['api_servers'] += 1
            
            return health_data
            
        except json.JSONDecodeError:
            return {'error': 'Invalid MCP configuration'}
    
    def get_backend_status(self):
        """Check backend application status."""
        status = {
            'exists': self.backend_dir.exists(),
            'has_main': (self.backend_dir / 'main.py').exists(),
            'has_requirements': (self.backend_dir / 'requirements.txt').exists(),
            'has_tests': (self.backend_dir / 'tests').exists(),
            'openapi_spec': (self.backend_dir / 'app' / 'openapi.json').exists()
        }
        
        if status['has_requirements']:
            try:
                with open(self.backend_dir / 'requirements.txt', 'r') as f:
                    requirements = f.read().strip().split('\n')
                status['dependency_count'] = len([r for r in requirements if r and not r.startswith('#')])
            except:
                status['dependency_count'] = 0
        
        return status
    
    def get_frontend_status(self):
        """Check frontend application status."""
        status = {
            'exists': self.frontend_dir.exists(),
            'has_package_json': (self.frontend_dir / 'package.json').exists(),
            'has_node_modules': (self.frontend_dir / 'node_modules').exists()
        }
        
        if status['has_package_json']:
            try:
                with open(self.frontend_dir / 'package.json', 'r') as f:
                    package_data = json.load(f)
                status['dependencies'] = len(package_data.get('dependencies', {}))
                status['dev_dependencies'] = len(package_data.get('devDependencies', {}))
                status['scripts'] = list(package_data.get('scripts', {}).keys())
            except:
                status['dependencies'] = 0
                status['dev_dependencies'] = 0
                status['scripts'] = []
        
        return status
    
    def get_recent_activity(self):
        """Get recent project activity."""
        try:
            # Get recent commits
            recent_commits = subprocess.run(
                ['git', 'log', '--since=7 days ago', '--oneline', '--format=%h|%an|%ad|%s'],
                capture_output=True, text=True, check=True
            ).stdout.strip().split('\n')
            
            commits = []
            for commit in recent_commits:
                if commit:
                    parts = commit.split('|')
                    if len(parts) >= 4:
                        commits.append({
                            'hash': parts[0],
                            'author': parts[1],
                            'date': parts[2],
                            'message': parts[3]
                        })
            
            return {
                'recent_commits': commits,
                'commit_count_7_days': len(commits)
            }
        except subprocess.CalledProcessError:
            return {'error': 'Could not fetch recent activity'}
    
    def generate_dashboard(self):
        """Generate comprehensive dashboard data."""
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'project_name': 'Awade',
            'git_stats': self.get_git_stats(),
            'documentation': self.get_documentation_status(),
            'mcp_health': self.get_mcp_health(),
            'backend': self.get_backend_status(),
            'frontend': self.get_frontend_status(),
            'activity': self.get_recent_activity()
        }
        
        return dashboard
    
    def print_dashboard(self):
        """Print a formatted dashboard to console."""
        dashboard = self.generate_dashboard()
        
        print("=" * 80)
        print("🎯 AWADE PROJECT DASHBOARD")
        print("=" * 80)
        print(f"📅 Generated: {dashboard['timestamp']}")
        print()
        
        # Git Statistics
        print("📊 GIT STATISTICS")
        print("-" * 40)
        if 'error' not in dashboard['git_stats']:
            git = dashboard['git_stats']
            print(f"📍 Branch: {git['current_branch']}")
            print(f"📝 Total Commits: {git['total_commits']}")
            print(f"📁 Total Files: {git['total_files']}")
            print(f"🐍 Python Files: {git['python_files']}")
            print(f"📚 Markdown Files: {git['markdown_files']}")
            print(f"🕐 Last Commit: {git['last_commit']['message']} ({git['last_commit']['hash']})")
        else:
            print("❌ Git repository not found")
        print()
        
        # Documentation Status
        print("📚 DOCUMENTATION STATUS")
        print("-" * 40)
        docs = dashboard['documentation']
        print(f"📋 Completeness: {docs['completeness']:.1f}% ({docs['present']}/{docs['total_required']})")
        
        if docs['missing']:
            print("❌ Missing files:")
            for file in docs['missing']:
                print(f"   - {file}")
        
        if docs['recent_updates']:
            print("🔄 Recently updated:")
            for update in docs['recent_updates'][:3]:
                print(f"   - {update['file']} ({update['modified']})")
        print()
        
        # MCP Health
        print("📡 MCP SERVER HEALTH")
        print("-" * 40)
        mcp = dashboard['mcp_health']
        if 'error' not in mcp:
            print(f"🖥️  Total Servers: {mcp['total_servers']}")
            print(f"📚 Documentation Servers: {mcp['documentation_servers']}")
            print(f"🔧 API Servers: {mcp['api_servers']}")
            
            print("📋 Server Types:")
            for server_type, count in mcp['server_types'].items():
                print(f"   - {server_type}: {count}")
        else:
            print(f"❌ {mcp['error']}")
        print()
        
        # Backend Status
        print("🔧 BACKEND STATUS")
        print("-" * 40)
        backend = dashboard['backend']
        print(f"📁 Backend exists: {'✅' if backend['exists'] else '❌'}")
        print(f"🐍 Main.py: {'✅' if backend['has_main'] else '❌'}")
        print(f"📦 Requirements: {'✅' if backend['has_requirements'] else '❌'}")
        print(f"🧪 Tests: {'✅' if backend['has_tests'] else '❌'}")
        print(f"📋 OpenAPI Spec: {'✅' if backend['openapi_spec'] else '❌'}")
        
        if backend['has_requirements']:
            print(f"📊 Dependencies: {backend['dependency_count']}")
        print()
        
        # Frontend Status
        print("🎨 FRONTEND STATUS")
        print("-" * 40)
        frontend = dashboard['frontend']
        print(f"📁 Frontend exists: {'✅' if frontend['exists'] else '❌'}")
        print(f"📦 Package.json: {'✅' if frontend['has_package_json'] else '❌'}")
        print(f"📚 Node modules: {'✅' if frontend['has_node_modules'] else '❌'}")
        
        if frontend['has_package_json']:
            print(f"📊 Dependencies: {frontend['dependencies']}")
            print(f"🔧 Dev Dependencies: {frontend['dev_dependencies']}")
            if frontend['scripts']:
                print(f"📜 Scripts: {', '.join(frontend['scripts'])}")
        print()
        
        # Recent Activity
        print("🔄 RECENT ACTIVITY")
        print("-" * 40)
        activity = dashboard['activity']
        if 'error' not in activity:
            print(f"📝 Commits (7 days): {activity['commit_count_7_days']}")
            
            if activity['recent_commits']:
                print("🕐 Recent commits:")
                for commit in activity['recent_commits'][:3]:
                    print(f"   - {commit['hash']}: {commit['message']} ({commit['author']})")
        else:
            print(f"❌ {activity['error']}")
        print()
        
        # Overall Health Score
        print("🏥 OVERALL HEALTH SCORE")
        print("-" * 40)
        
        score = 0
        max_score = 100
        
        # Documentation completeness (30 points)
        docs_score = dashboard['documentation']['completeness'] * 0.3
        score += docs_score
        
        # Git activity (20 points)
        if 'error' not in dashboard['git_stats']:
            git_score = min(20, dashboard['git_stats']['total_commits'] / 10)
            score += git_score
        
        # MCP configuration (20 points)
        if 'error' not in dashboard['mcp_health']:
            mcp_score = min(20, dashboard['mcp_health']['total_servers'] * 2)
            score += mcp_score
        
        # Backend setup (15 points)
        backend_score = sum([
            5 if dashboard['backend']['has_main'] else 0,
            5 if dashboard['backend']['has_requirements'] else 0,
            5 if dashboard['backend']['has_tests'] else 0
        ])
        score += backend_score
        
        # Frontend setup (15 points)
        frontend_score = sum([
            5 if dashboard['frontend']['exists'] else 0,
            5 if dashboard['frontend']['has_package_json'] else 0,
            5 if dashboard['frontend']['has_node_modules'] else 0
        ])
        score += frontend_score
        
        print(f"🎯 Health Score: {score:.1f}/{max_score}")
        
        if score >= 80:
            print("🌟 Excellent! Project is in great shape!")
        elif score >= 60:
            print("✅ Good! Project is well-structured.")
        elif score >= 40:
            print("⚠️  Fair. Some improvements needed.")
        else:
            print("❌ Needs attention. Review missing components.")
        
        print("=" * 80)
    
    def save_dashboard(self, filename=None):
        """Save dashboard data to JSON file."""
        if filename is None:
            filename = f"logs/dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        self.logs_dir.mkdir(exist_ok=True)
        
        dashboard = self.generate_dashboard()
        
        with open(filename, 'w') as f:
            json.dump(dashboard, f, indent=2)
        
        print(f"📄 Dashboard saved to {filename}")
        return filename

def main():
    """Main function to run the monitoring dashboard."""
    monitor = AwadeMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--save':
        filename = monitor.save_dashboard()
        print(f"✅ Dashboard saved to {filename}")
    else:
        monitor.print_dashboard()

if __name__ == "__main__":
    main() 