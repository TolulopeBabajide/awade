# Awade Comprehensive Architecture Diagram

This document contains a more detailed representation of the Awade system architecture, including the latest additions like Gemini support, Admin RBAC, and hybrid cloud deployment.

## High-Level Architecture (Mermaid)

```mermaid
graph TB
    subgraph "User Layer"
        User[("Educator / Admin")]
    end

    subgraph "Frontend Layer (Vercel)"
        FE["React SPA (Vite + TS)"]
        AuthContext["Auth Context / RBAC"]
        APIService["API Service (Axios)"]
    end

    subgraph "Backend API Layer (Railway)"
        API["FastAPI App"]
        RouterAuth["Auth Router (JWT/Google)"]
        RouterLesson["Lesson Plan Router"]
        RouterAdmin["Admin Router (Moderation/Logs)"]
        
        API --> RouterAuth
        API --> RouterLesson
        API --> RouterAdmin
    end

    subgraph "Async Processing Layer (Railway)"
        Redis[("Redis Queue")]
        Worker["Arq Worker"]
        Exporter["Export Service (PDF/DOCX)"]
    end

    subgraph "Data Layer (Railway)"
        DB[("Postgres (SQLAlchemy)")]
    end

    subgraph "AI Core (Monorepo Package)"
        AICore["packages/ai"]
        OpenAIProvider["OpenAI Provider"]
        GeminiProvider["Gemini Provider"]
        AICache["Prompt/Response Cache"]
    end

    subgraph "External Providers"
        OpenAI[("OpenAI API")]
        Gemini[("Google Gemini API")]
        GoogleOAuth[("Google OAuth")]
    end

    %% Connections
    User -->|HTTPS| FE
    FE --> AuthContext
    FE --> APIService
    APIService -->|REST API| API
    
    API --> DB
    RouterAuth --> GoogleOAuth
    
    RouterLesson -->|Enqueue Task| Redis
    Redis --> Worker
    Worker --> AICore
    Worker --> Exporter
    
    AICore --> AICache
    AICore --> OpenAIProvider
    AICore --> GeminiProvider
    
    OpenAIProvider --> OpenAI
    GeminiProvider --> Gemini
    
    Worker -->|Update Status/Save Content| DB
```

## Component Breakdown

1.  **Frontend (React/Vite)**: Hosted on Vercel. Managed independently for fast iteration.
2.  **Backend (FastAPI)**: Hosted on Railway. Unified API handling the monorepo logic.
3.  **Packages**: 
    - `packages/ai`: Encapsulates multi-provider AI logic, retry strategies, and response fixing.
4.  **Worker (Arq)**: Offloads heavy AI generation and document exporting to background threads.
5.  **Multi-Model Strategy**: Seamlessly switches or tiers between OpenAI and Gemini for cost/performance optimization. 
