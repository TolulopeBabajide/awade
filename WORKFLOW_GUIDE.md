# Awade Development Workflow Guide

## 🚀 Quick Start

1. **Setup**: Run `./scripts/setup_workflow.sh` to install dependencies
2. **Development**: Make changes to your code
3. **Commit**: Git hooks will automatically validate and update docs
4. **Health Check**: Run `python3 scripts/mcp_health_check.py` to check MCP status

## 🔧 Available Scripts

### `scripts/update_api_docs.py`
- Automatically updates API documentation when backend files change
- Generates OpenAPI specification
- Validates documentation links

### `scripts/mcp_health_check.py`
- Checks MCP server configuration and health
- Validates server endpoints
- Generates health reports

### `scripts/setup_workflow.sh`
- Installs required dependencies
- Configures Git hooks
- Sets up directory structure

## 📋 Git Hooks

### Pre-commit Hook
Automatically runs before each commit:
- ✅ Validates required documentation files exist
- ✅ Checks for API documentation updates
- ✅ Prevents committing sensitive files (.env)
- ✅ Validates MCP configuration
- ✅ Runs health checks

## 🏥 Health Monitoring

Run health checks manually:
```bash
# Basic health check
python3 scripts/mcp_health_check.py

# Save health report
python3 scripts/mcp_health_check.py --save
```

## 📊 Reports

Health reports are saved to `logs/mcp_health.json` for tracking over time.

## 🔄 Automation

The workflow automatically:
- Updates API docs when backend changes
- Validates documentation integrity
- Monitors MCP server health
- Prevents common commit mistakes

## 🆘 Troubleshooting

### Common Issues

1. **Pre-commit hook fails**: Check that all required docs exist
2. **API docs not updating**: Ensure backend files are properly staged
3. **MCP health check fails**: Verify `.cursor/mcp.json` configuration

### Manual Override

To skip pre-commit checks (not recommended):
```bash
git commit --no-verify -m "your message"
```
# Test commit to verify pre-commit hook
