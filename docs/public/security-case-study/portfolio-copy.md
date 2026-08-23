# Awade Security Case Study — Portfolio Copy Pack

## Project-card copy

### Title

**Securing Awade's Identity, Child Data and AI Boundaries**

### Short description

I threat-modelled an AI education platform, hardened authentication and child-data authorization, and validated its model safeguards with focused security tests.

### Technical alternative

How I secured a React and FastAPI application with JWT authentication, role and ownership checks, Redis token revocation, prompt-injection defences and validated AI output.

## Full portfolio introduction

Awade helps African teachers build curriculum-aligned lesson resources and gives parents practical guides for supporting a child's learning at home. That makes identity, child data and AI-generated content central security concerns rather than secondary infrastructure details.

I reviewed the platform from the browser through FastAPI, PostgreSQL, Redis and its OpenAI/Gemini provider layer. I traced authentication, role enforcement, child-profile ownership, session revocation, administrative actions, AI input and output, and PDF export to the code that actually enforces each boundary.

The resulting case study demonstrates layered application and AI security: fixed-algorithm JWT validation, HttpOnly cookies, Redis-backed refresh-token revocation, route-level RBAC, owner-scoped data access, enumeration-resistant auth flows, rate-limited generation, prompt sanitisation, delimited data blocks and structured output safety checks. Focused validation completed with 182 tests passing and no new Critical or High findings.

## CV bullet

Reviewed and hardened a React/FastAPI education platform across JWT authentication, RBAC, child-data ownership and OpenAI/Gemini boundaries, implementing Redis-backed token revocation, rate-limited sensitive routes, prompt-injection defences and schema-validated AI output backed by 182 focused security tests.

## Short CV bullet

Threat-modelled and secured a FastAPI/PostgreSQL AI platform using JWT/RBAC, owner-scoped child data, Redis token revocation and validated LLM input/output controls.

## GitHub repository description

Evidence-backed security case study for an AI education platform: JWT, RBAC, child-data ownership, token revocation and LLM safety controls.

## Suggested GitHub topics

`application-security` · `api-security` · `ai-security` · `fastapi` · `postgresql` · `jwt` · `rbac` · `redis` · `prompt-injection` · `owasp-llm` · `child-privacy`

## LinkedIn launch post

I built Awade to help African teachers and parents turn curriculum topics into practical learning support. Then I reviewed it as a security system, not just a product.

The platform handles account identities, child profiles, role-restricted administration and AI-generated educational content. I traced those boundaries from the React client through FastAPI, PostgreSQL, Redis and the model-provider layer.

The review covered:

- JWT validation and HttpOnly-cookie sessions;
- role-based and child-record ownership checks;
- Redis-backed refresh-token revocation;
- enumeration-resistant authentication flows;
- rate limits on auth, generation and export routes;
- prompt-injection sanitisation and data delimiters;
- structured, child-safety-aware model-output validation; and
- secure PDF-generation boundaries.

Focused security validation completed with 182 tests passing and no new Critical or High findings.

I also documented what remains—especially AI key-rotation evidence and ongoing dependency and jurisdiction reviews—because good security work includes the unfinished parts.

## Short LinkedIn alternative

Security case study published: I threat-modelled Awade's React, FastAPI, PostgreSQL, Redis and AI architecture.

The strongest controls are composable authorization—authentication, active-account status, role and record ownership checked separately—and a model boundary that treats both input and output as untrusted.

The evidence: 182 focused security tests passed, with no new Critical or High findings. The publication includes the residual risks too. No “secure by AI” slogans. Just controls, tests and honest limitations.

> 📝 **Feedback prompt**: If you revise this output significantly before using it, please log it — `"Log feedback: security-agent output was [approved / revised / rejected] — [what changed]"`
