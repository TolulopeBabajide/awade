# Privacy Policy — Awade

**Effective date:** 1 May 2026
**Last updated:** 4 May 2026

Awade ("we", "us", "our") is committed to protecting the privacy of everyone who uses our platform — parents, educators, and the children whose learning we support. This policy explains what data we collect, how we use it, where we store it, and the rights you have over it.

If you have questions, contact us at **privacy@awade.org**.

---

## 1. Who We Are

Awade is an AI-powered learning platform that helps African parents support their children's schoolwork, and gives teachers curriculum-aligned lesson plans. Our services are operated by the Awade team. For data-protection purposes, Awade is the **data controller** (GDPR / POPIA) and the **data controller** (NDPR).

---

## 2. What Data We Collect

### 2a. Account data
- Name, email address, and password (hashed — we never store plaintext passwords).
- Role (parent or educator) and registration date.
- Google account ID and profile picture if you sign in with Google.
- Phone number (optional — only stored if you add it in Settings).

### 2b. Child profile data (parents only)
- Child's first name, country, curriculum, grade level, and selected subjects.
- This data is **parent-mediated** — children do not create accounts or interact with Awade directly. We do not knowingly collect data directly from children under 13.

### 2c. AI-generated content
- "How to Help" guides generated for a specific child and topic, linked to your account.
- Educator lesson plans, lesson resources, and associated topics.

### 2d. Usage and technical data
- Log data (timestamps, API endpoints called, HTTP status codes) — no personally identifying request bodies are logged.
- Error events forwarded to our error-monitoring service (Sentry) — stack traces and request metadata only; no passwords or child names are included in error payloads.
- Browser and device type, inferred from your User-Agent header.
- **Page analytics collected by Vercel Analytics** (our frontend hosting provider): page URL visited, referrer URL, device type (mobile / desktop / tablet), and country inferred from your IP address. Vercel Analytics operates **without cookies** and does not fingerprint individual users. Raw IP addresses are not stored by Vercel; only the derived country is retained. You can opt out by sending a `DNT: 1` (Do Not Track) header in your browser.

### 2e. What we do NOT collect
- Payment card or bank details (we do not yet process payments).
- Location beyond the country you provide when creating a child profile.
- Photos, audio, or video.
- School names or teacher identification numbers unless you add them voluntarily.

---

## 3. How We Use Your Data

| Purpose | Legal basis |
|---------|------------|
| Deliver the service (generate guides, lesson plans, save content; store optional profile fields such as phone number if provided) | Contract performance |
| Authenticate your account and maintain session security | Contract performance / legitimate interest |
| Monitor platform health and debug errors (Sentry) | Legitimate interest |
| Improve AI prompt quality using aggregated, anonymised interaction data | Legitimate interest |
| Measure platform usage (page views, device type, country) via Vercel Analytics — cookieless, no individual-user tracking | Legitimate interest |
| Comply with legal obligations (tax, audit, court orders) | Legal obligation |
| Send product and service updates you have opted into | Consent |

We do **not** use your data for advertising, and we do not sell personal data to third parties.

---

## 4. Data Residency and International Transfers

> **This section addresses the specific requirements of Nigeria's NDPR (2019), South Africa's POPIA (2013 / commenced 2021), and the EU GDPR (2018).**

### 4a. Where your data is stored

| Data type | Storage system | Region |
|-----------|---------------|--------|
| User accounts, child profiles, parent guides, lesson plans | PostgreSQL on Render (managed cloud database) | **United States (Oregon, US West)** |
| API application server | Render web service | **United States (Oregon, US West)** |
| Frontend static assets | Vercel CDN | **Global edge network (primary origin: United States)** |
| Error and diagnostic logs | Sentry (sentry.io) | **United States** |
| AI content generation | OpenAI API | **United States** |

All data at rest is encrypted (AES-256). All data in transit uses TLS 1.2 or higher.

### 4b. Cross-border transfer safeguards

Awade's primary users are in Africa, but our infrastructure currently resides in the United States. We acknowledge that this constitutes a **cross-border transfer** under:

- **NDPR (Nigeria)**: Article 2.11 of the NDPR Implementation Framework requires that cross-border transfers of personal data occur only to countries with an adequate level of protection or where the data subject has given informed consent. By using Awade and accepting this policy, Nigerian users **give explicit, informed consent** to the transfer of their personal data (including child profile data) to the United States for the purposes described above. We apply contractual safeguards with all sub-processors (see §4c).

- **POPIA (South Africa)**: Section 72 of POPIA requires that personal information may only be transferred to a third country if that country has adequate data-protection laws, the data subject consents, or the transfer is necessary for the performance of a contract. By using Awade and accepting this policy, South African users **give explicit, informed consent** to the transfer of their personal data to the United States. We apply binding contractual safeguards with all sub-processors and maintain this policy as a public disclosure of transfer destination.

- **GDPR (EU/EEA)**: Transfers to the United States rely on **Standard Contractual Clauses (SCCs)** with sub-processors where applicable, and on explicit consent from EU-based users.

### 4c. Sub-processors

| Sub-processor | Purpose | Location | Data shared |
|---------------|---------|----------|------------|
| Render (Render Services, Inc.) | Application hosting and managed PostgreSQL | United States | All user and child profile data |
| Vercel, Inc. | Frontend hosting, CDN, and cookieless page analytics (Vercel Analytics) | United States | Page URL, referrer URL, device type, IP-derived country (raw IPs not stored by Vercel) |
| OpenAI, LLC | AI guide and lesson plan generation | United States | Child grade level, subject, and topic (no names or identifying data sent to OpenAI) |
| Sentry (Functional Software, Inc.) | Error monitoring | United States | Stack traces, request metadata (no passwords, no child names) |

We do not share personal data with any other third party unless required by law.

### 4d. Data minimisation before AI processing

When generating an AI guide, we send **only** the child's grade level, subject, and topic to OpenAI — not the child's name, country, or any other identifying information. This is a deliberate COPPA and NDPR / POPIA data-minimisation measure.

### 4e. Future data residency plans

We intend to offer Africa-region hosting (e.g. via a provider with data centres in South Africa or Nigeria) as the platform scales. When that option becomes available, we will notify users and offer migration of their data. This policy will be updated to reflect any change in storage region.

---

## 5. Children's Privacy (COPPA / NDPR / POPIA)

Awade supports learning for children but does **not** collect data directly from children. All child data (name, grade, country, subjects) is entered by a parent or guardian on behalf of the child. We therefore treat this data as **parent-provided** and apply the following protections:

- Child names are never included in AI prompts sent to OpenAI.
- Child profile data is visible only to the authenticated parent who created it. Administrators can view structural fields (grade, country) for compliance auditing only — guide content is excluded from admin views.
- Parents can delete all child profiles and associated guides at any time (GDPR right to erasure, NDPR right to withdrawal of consent, POPIA right to destruction).
- We do not retain child data beyond the lifetime of the parent's account.

---

## 6. Data Retention

| Data type | Retention period |
|-----------|-----------------|
| Account data | Duration of account + 30 days after deletion request |
| Child profiles and guides | Duration of parent account + 30 days after deletion request |
| Server access logs | 90 days |
| Error logs (Sentry) | 90 days |
| Anonymised, aggregated usage statistics | Indefinitely (no PII retained) |

---

## 7. Your Rights

Depending on your country, you may have the following rights. To exercise any of them, email **privacy@awade.org**.

| Right | GDPR | NDPR | POPIA |
|-------|------|------|-------|
| Access (receive a copy of your data) | ✅ Art. 15 | ✅ Art. 2.7 | ✅ Sec. 23 |
| Rectification (correct inaccurate data) | ✅ Art. 16 | ✅ Art. 2.7 | ✅ Sec. 24 |
| Erasure / destruction (delete your data) | ✅ Art. 17 | ✅ Art. 2.8 | ✅ Sec. 24 |
| Portability (receive data in machine-readable format) | ✅ Art. 20 | ✅ | — |
| Objection to processing | ✅ Art. 21 | ✅ | ✅ Sec. 11 |
| Withdraw consent | ✅ Art. 7(3) | ✅ Art. 2.9 | ✅ Sec. 11 |

We will respond to all requests within **30 days**. For complex requests we may extend this by a further 30 days with notice.

---

## 8. Security

We implement the following technical and organisational measures:

- All data in transit protected by TLS 1.2+.
- Database encrypted at rest (Render managed PostgreSQL, AES-256).
- Passwords stored as bcrypt hashes (never in plaintext).
- JWT access tokens carried in HttpOnly, Secure, SameSite=Lax cookies — not in localStorage.
- Role-based access control: parent data is accessible only to the authenticated parent; admin access is logged.
- Rate limiting on authentication endpoints to limit brute-force attacks.
- Dependency vulnerability scanning on CI (npm audit, pip-audit).
- Regular security audits (see `docs/agentic/audits/`).

---

## 9. Cookies and Analytics

We use the following cookies:

| Cookie | Purpose | Duration |
|--------|---------|----------|
| `access_token` | Authentication (HttpOnly, Secure) | Session / JWT expiry |
| `refresh_token` | Session renewal (HttpOnly, Secure) | 7 days |

We do not use advertising cookies. We do not use analytics cookies.

**Vercel Analytics** — our hosting provider collects basic page-view statistics (page URL, referrer, device type, IP-derived country) to help us understand how the platform is used. Vercel Analytics does **not** use cookies and does not build individual user profiles. Raw IP addresses are processed transiently to derive country and are not retained. You can signal opt-out by enabling the **Do Not Track (DNT)** setting in your browser; Vercel Analytics respects the `DNT: 1` header.

If we add any advertising or cookie-based analytics in future, we will update this policy and request fresh consent before enabling them.

---

## 10. Changes to This Policy

We will notify you of material changes by email (if you have an account) and by updating the "Last updated" date at the top of this document. Continued use of Awade after the effective date of a revised policy constitutes acceptance of the changes.

---

## 11. Contact and Complaints

**Privacy enquiries:** privacy@awade.org

**Nigerian users:** If you believe we have processed your personal data in breach of the NDPR, you may lodge a complaint with the **Nigeria Data Protection Commission (NDPC)** at [ndpc.gov.ng](https://ndpc.gov.ng).

**South African users:** If you believe we have processed your personal data in breach of POPIA, you may lodge a complaint with the **Information Regulator (South Africa)** at [inforegulator.org.za](https://www.inforegulator.org.za).

**EU/EEA users:** You may lodge a complaint with your local **Data Protection Authority (DPA)**.

---

*Awade is committed to African-centred, privacy-respecting education technology. We welcome feedback on this policy at privacy@awade.org.*
