# Awade

**Awade** is an AI-powered educator support platform built to empower African teachers with curriculum-aligned lesson planning, localized training, and reflective teaching tools. It emphasizes ethical AI integration, offline usability, and professional development that respects local context.

## 🌍 Project Overview

Awade bridges the professional development gap by:

- **Generating structured 6-section lesson plans** with AI-powered curriculum alignment
- **Integrating local context** for culturally relevant, practical teaching resources
- **Providing curriculum-aligned micro-training modules**
- **Enabling offline access and local language support**
- **Prioritizing teacher agency and explainable AI interactions**

Built as a modular and extensible platform using a monorepo structure.

## 🎯 User Workflow

The complete user journey follows this flow:
1. **Sign Up / Log In** → 2. **Dashboard** → 3. **Select Subject, Grade & Topic** → 4. **Input Local Context** → 5. **Generate Lesson Plan** → 6. **Edit Lesson Plan** → 7. **Export (PDF/DOC)** → 8. **Offline Use in Class**

For detailed workflow documentation, see [docs/internal/project-workflow.md](./docs/internal/project-workflow.md).

### 🎯 Key Features

- **Structured Lesson Plans**: AI generates 6-section plans (Learning Objectives, Local Context, Core Content, Activities, Quiz, Related Projects)
- **Local Context Integration**: Adapts lessons to local environment, available resources, and community needs
- **Curriculum Mapping**: Country-specific curriculum standards integration
- **PDF Export**: Professional lesson plan export with WeasyPrint
- **Offline Support**: Works without internet connectivity

## 🛠️ Setup Guide

### Requirements
- Python 3.10+
- Node.js (for frontend)
- PostgreSQL
- Cursor (recommended for dev)

### Installation Steps

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/awade.git
   cd awade
   ```

2. **Install backend dependencies**
   ```bash
   cd apps/backend
   pip install -r requirements.txt
   ```

3. **Install frontend (optional HTML or React setup)**
   ```bash
   cd apps/frontend
   npm install
   npm run dev
   ```

4. **Create .env file**
   ```bash
   cp .env.example .env
   ```
   Fill in your keys and DB URL.

5. **Run backend**
   ```bash
   uvicorn main:app --reload
   ```

### CI/CD Setup

For GitHub Actions to work properly, set up the following secrets in your repository:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Application secret key  
- `OPENAI_API_KEY`: OpenAI API key

Go to Settings → Secrets and variables → Actions to configure these.

## 🏗 Architecture

```
awade/
├── apps/
│   ├── frontend/        # Mobile-friendly UI (HTML/Pug/React)
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
- ❌ AI model training or dataset usage is prohibited. See [AI_USE_POLICY.md](./AI_USE_POLICY.md)

## 🔒 Security

- **Never hard-code secrets**: Use environment variables and GitHub Secrets
- **Security guidelines**: See [docs/internal/security-guidelines.md](./docs/internal/security-guidelines.md)
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
