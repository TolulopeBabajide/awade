# Awade Documentation

This directory contains all documentation for the Awade project, organized by visibility and purpose.

## 📁 Directory Structure

### `public/` - Public Documentation
These documents are safe for public consumption and help users and developers understand the platform.

**Available Documentation:**
- **`external/`** - User-facing documentation
  - `user-guide.md` - Complete user guide for the platform
  - `faq.md` - Frequently asked questions
- **`user-guide/`** - Role-specific user guides
  - `teacher.md` - Guide for teachers
  - `admin.md` - Guide for administrators
  - `lesson-planning.md` - Lesson planning guide
  - `analytics.md` - Analytics and reporting guide
  - `user-management.md` - User management guide
  - `training.md` - Training and professional development guide
- **`api/`** - API documentation
  - `README.md` - API overview and getting started
  - `database.md` - Database schema documentation
  - `ai-integration.md` - AI integration guide
- **`development/`** - Development documentation
  - `README.md` - Development setup and guidelines
  - `contributing.md` - Contribution guidelines
  - `frontend.md` - Frontend development guide
- **`deployment/`** - Deployment documentation
  - `README.md` - Deployment guide

### `private/` - Private Documentation ⚠️
These documents contain sensitive information, internal architecture details, and development specifications that should not be exposed publicly.

**Private Documentation (Internal Use Only):**
- **`authentication-authorization.md`** - Internal auth system details
- **`requirements.md`** - Detailed project requirements and specifications
- **`security-guidelines.md`** - Internal security protocols and guidelines
- **`lesson-plan-architecture.md`** - Internal lesson plan system architecture
- **`project-workflow.md`** - Internal development workflow
- **`curriculum-mapping-system.md`** - Internal curriculum system details
- **`erd-structure.md`** - Database entity relationship diagrams
- **`curriculum-database-guide.md`** - Internal database guide
- **`api-contracts.md`** - Internal API contract specifications
- **`contract-testing.md`** - Internal testing protocols
- **`testing.md`** - Internal testing guidelines
- **`schema-fixes-summary.md`** - Internal schema change documentation
- **`curriculum-mapping-acceptance-criteria.md`** - Internal acceptance criteria
- **`documentation-coverage-summary.md`** - Internal documentation analysis
- **`doc-coverage.md`** - Internal documentation coverage metrics

## 🚨 Security Notice

**Never commit private documentation to public repositories!** These documents may contain:
- Internal system architecture details
- Security protocols and guidelines
- Database schemas and relationships
- API contract specifications
- Development workflow details
- Testing strategies and acceptance criteria

## 📖 Documentation Guidelines

### For Public Documentation
- **User-focused**: Write for end users and external developers
- **Clear and concise**: Use simple language and examples
- **Comprehensive**: Cover all necessary topics for public use
- **Up-to-date**: Keep documentation current with the codebase

### For Private Documentation
- **Internal use only**: Never expose to public repositories
- **Detailed specifications**: Include technical details and architecture
- **Security-conscious**: Include security guidelines and protocols
- **Development-focused**: Include workflow and testing details

## 🔒 Access Control

### Public Documentation
- ✅ Available to all users and developers
- ✅ Can be referenced in public repositories
- ✅ Safe for external sharing and collaboration

### Private Documentation
- 🔒 Internal use only
- 🔒 Protected by `.gitignore`
- 🔒 Contains sensitive information
- 🔒 Should be stored in private repositories or secure locations

## 📝 Contributing to Documentation

When adding new documentation:

1. **Determine visibility**:
   - **Public**: User guides, API docs, development setup
   - **Private**: Internal architecture, security, testing details

2. **Place in appropriate directory**:
   - Public docs → `docs/public/`
   - Private docs → `docs/private/`

3. **Follow guidelines**:
   - Use clear, consistent formatting
   - Include examples where helpful
   - Keep documentation current

4. **Security considerations**:
   - Never include hardcoded secrets
   - Use placeholder examples
   - Review for sensitive information before committing

## 🛠️ Documentation Tools

- **Coverage Analysis**: Use `scripts/private/doc_coverage.py` to analyze documentation coverage
- **API Documentation**: Auto-generated from OpenAPI specifications
- **Markdown Linting**: Ensure consistent formatting
- **Link Validation**: Check for broken links and references

## 📚 Documentation Standards

### Markdown Guidelines
- Use consistent heading structure
- Include table of contents for long documents
- Use code blocks with language specification
- Include examples and screenshots where helpful

### File Naming
- Use kebab-case for file names
- Include descriptive names
- Group related documentation in subdirectories

### Content Organization
- Start with overview and purpose
- Include step-by-step instructions
- Provide troubleshooting sections
- Include references and links 