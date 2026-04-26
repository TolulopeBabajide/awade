# Awade System Architecture

## Visual Overview

![Awade System Architecture Mockup](/Users/tolulopebabajide/.gemini/antigravity/brain/a72c1f83-3602-44c4-91bb-503e90fc2a47/awade_architecture_diagram_1773230035374.png)

## System Context

Awade is an AI-powered educator support platform designed to help African teachers generate curriculum-aligned lesson plans. The system integrates with both OpenAI and Google Gemini for content generation and provides a structured way to manage curriculum data.

```mermaid
graph TB
    subgraph "Client Layer"
        User[Educator] -->|HTTPS/REST| FE[Frontend (React/Vite)]
    end
    
    subgraph "Backend Layer (Railway)"
        FE -->|API Calls| API[Backend API (FastAPI)]
        API -->|CRUD| DB[(PostgreSQL)]
        API -->|Task Queue| Redis[(Redis)]
        Redis -->|Consume| Worker[Arq Worker]
    end
    
    subgraph "AI Core Layer"
        Worker -->|Request| AICore[packages/ai]
        AICore -->|OpenAI| OAI[OpenAI Service]
        AICore -->|Gemini| GEM[Gemini Service]
    end
```

## Backend Architecture

The backend is built with **FastAPI** following a modular service-oriented pattern.

### Directory Structure
- **`routers/`**: Handle HTTP requests, validation (Pydantic schemas), and permission checks (Dependencies).
- **`services/`**: Contain core business logic. Separation of concerns ensures routers stay thin.
- **`models/`**: SQLAlchemy ORM definitions mapping to PostgreSQL tables.
- **`schemas/`**: Pydantic models for request/response serialization.
- **`packages/ai/`**: specialized module for AI integration.

### Key Components
1.  **LessonPlanService**: Manages the lifecycle of lesson plans and delegates resource generation to the task queue.
2.  **AuthService**: Handles JWT issuance, Refresh Token Rotation, Google OAuth verification, and user management. Includes Rate Limiting on authentication endpoints.
3.  **AdminService & Routers**: Implements RBAC (Role Based Access Control) distinguishing Admin and Super Admin roles, handling analytics, moderation (flagging/approving generated content), and template administration. Includes Audit Logging.
4.  **GPTService**: Wrapper around Provider API interfaces (OpenAI, Gemini), handling prompt construction, retries, JSON repairing, and schema validation.
5.  **Worker**: An `arq` worker process that handles long-running tasks like "Generate Lesson Resource" to prevent blocking API threads. Support for Background Worker status tracking.

### Async Task Flow
1.  User requests "Generate Resources".
2.  `LessonPlanService` creates a record with `status='processing'` and enqueues a job in Redis.
3.  API returns immediately with the resource ID.
4.  Worker picks up the job, calls `GPTService`, updates the DB record with content and `status='completed'`.
5.  Frontend polls (or uses simplified re-fetching) to get the completed resource.

## Frontend Architecture

The frontend is a **React** single-page application (SPA) built with **Vite** and **TypeScript**.

- **Styling**: Tailwind CSS for utility-first styling.
- **State Management**: React Context (e.g., AuthContext) and local state. Complex server state is managed via `useEffect` and service calls.
- **API Layer**: Centralized `api.ts` service (axios instance) handles all network requests, error interception, and token attachment.
- **Routing**: React Router DOM.

## Database Schema

The PostgreSQL database uses a relational schema centered around **Curriculum** and **Users**.

- **Core Hierarchy**: `Country` -> `Curriculum` -> `CurriculumStructure` (linking Subject & Grade) -> `Topic`.
- **User Data & Auth**: `User` -> `LessonPlan` -> `LessonResource`. Redis handles token revocation lists.
- **Admin**: `AdminAuditLog` tracking administrative actions, `ResourceModeration` handling moderation reviews of AI output, `LessonTemplate` managing active prompt structures.
- **Context**: `Context` table stores local relevance data injected into AI prompts.

## AI Integration

AI logic is encapsulated in `packages/ai`.
- **Prompts**: Stored as templates to allow easy modification without code changes.
- **Service**: Handles API communication, mock fallbacks (when API key is missing), and response validation.
