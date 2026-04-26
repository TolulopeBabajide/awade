# Awade

**Awade** is an AI-powered educator support platform that helps African teachers generate curriculum-aligned lesson plans with local context. It emphasizes ethical AI integration and practical classroom readiness.

## 🌍 Project Overview

Awade currently supports:

- **Generating structured lesson plans** with AI-powered curriculum alignment
- **Integrating local context** for culturally relevant, practical teaching resources
- **Managing curriculum data** (countries → curricula → subjects/grades → topics)
- **Generating lesson resources** attached to lesson plans
- **Exporting lesson resources** to PDF/DOCX

Built as a modular and extensible platform using a monorepo structure.

## 🎯 User Workflow

The complete user journey follows this flow:
1. **Sign Up / Log In** → 2. **Dashboard** → 3. **Select Subject, Grade & Topic** → 4. **Input Local Context** → 5. **Generate Lesson Plan** → 6. **Edit Lesson Plan** → 7. **Export (PDF/DOC)** → 8. **Offline Use in Class**

For detailed workflow documentation, see [docs/public/development/README.md](./docs/public/development/README.md).

### 🎯 Key Features (Implemented)

- **Structured Lesson Plans**: AI-assisted generation using GPT with local context
- **Local Context Integration**: Store and reuse context per lesson plan
- **Curriculum Mapping**: Country, curricula, subject, grade-level, topic structure
- **Lesson Resources**: AI-generated JSON content persisted per plan
- **PDF/DOCX Export**: WeasyPrint-based export service
- **Performance**: LRU/LFU caching and query optimization utilities
- **Security**: Input validation, SQL injection prevention, and rate limiting

### 🧭 Roadmap (Planned, not yet implemented)

- Training modules and progress tracking
- Gamification (achievements, streaks, leaderboards)
- Student-facing learning experience
- Offline-first experience and sync
- Multi-language UI switching
- Analytics dashboard and usage insights
- Full-text search and indexing

## 🛠️ Setup Guide

Please refer to the detailed [Development Setup Guide](./docs/public/development/README.md) for full instructions on setting up Docker, Python, Node, and environment variables.

## 🏗 Architecture

```
awade/
├── apps/
│   ├── frontend/        # React + TypeScript frontend
│   └── backend/         # FastAPI backend
├── packages/
│   ├── ai/              # Prompt templates, GPT logic, rules
│   └── shared/          # Reusable models and helpers
├── scripts/             # Setup and automation scripts
├── .env.example         # Sample environment file
└── README.md            # Project info and setup
```

## 📜 Licensing & AI Use

- 🧠 Code: [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html)
- 📘 Content: [CC-BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
- ❌ AI model training or dataset usage is prohibited. See [ai-use-policy.md](./docs/public/external/ai-use-policy.md)

## 🔒 Security

- **Never hard-code secrets**: Use environment variables and GitHub Secrets
- **Security guidelines**: See [SECURITY.md](./SECURITY.md)
- **Data Structure Security**: All caching and data structures are thread-safe with comprehensive input validation
- **SQL Injection Prevention**: Advanced query validation and sanitization
- **Rate Limiting**: Built-in protection against abuse and DoS attacks
- **Memory Protection**: Bounded memory usage with configurable limits
- **Input Sanitization**: All user inputs are validated and sanitized before processing
- **Environment setup**: Copy `.env.example` to `.env` and fill in your values

## 🤝 Contribution Guide

### 1. Fork & Clone
Make your changes in a feature branch:
```bash
git checkout -b feature/your-feature-name
```

### 2. Follow Conventions
- **Python**: Black formatter, type hints, docstrings
- **Frontend**: Semantic HTML or React components with Tailwind (if used)
- **Commits**: Conventional commits (feat:, fix:, chore:)

### 3. Testing
Run local tests before pushing:
```bash
pytest
```

### 4. Pull Request
Submit a PR to develop branch. Include:
- Summary of what you changed
- Screenshots if UI-related
- Link to issue (if tracked)

We welcome contributors in all forms—educators, developers, translators, voice artists, and learners.
