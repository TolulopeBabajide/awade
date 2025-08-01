# Awade MVP Test Plan

This document outlines the testing strategy, test cases, and tools to validate the Awade platform MVP during development and before submission.

---

## 🎯 Objectives

- Ensure all core features function as intended
- Validate performance and usability in low-bandwidth environments
- Confirm ethical and explainable AI behavior
- Identify edge cases and minimize user friction

---

## 🧪 Testing Types

| Type                | Purpose                                                        |
| ------------------- | -------------------------------------------------------------- |
| Functional Testing  | Validate all features perform according to user stories        |
| Usability Testing   | Ensure intuitive design and accessibility                      |
| Unit Testing        | Test individual backend functions and AI logic                 |
| Integration Testing | Validate communication between backend and frontend components |
| Manual Think-Aloud  | Collect qualitative feedback during live use                   |
| Lighthouse Tests    | Audit performance, accessibility, SEO, and best practices      |

---

## ✅ Test Cases Overview

### 1. Lesson Plan Generator
- Input: Subject, Grade, Topic → Output: Structured Plan
- Verify: Editable UI, Explanation Section, Export Works

### 2. Micro-Training Module Viewer
- Load training content, update progress, reflect completion
- Edge: Handle offline mode; resume after disconnect

### 3. Offline Mode
- Cache module/lesson
- Check sync status, retry if failed

### 4. User Profile and Localization
- Update language, grade level
- Confirm UI switches and relevant content updates

### 5. AI Feedback & Control
- Accept/Edit/Reject suggestions
- Track behavior for personalization logic

### 6. Bookmarks & Community Highlights
- Bookmark lessons, view community feed
- Test save/reload functionality

---

## 🧪 Tools Used

- **Cursor Agent** – dev/test generation
- **Postman** – backend API testing
- **Playwright / Selenium** – UI testing
- **Lighthouse CLI** – performance & accessibility audit
- **User testing form** – feedback collection

---

## 📋 Deliverables

- Test Report with passed/failed results
- Screenshots or videos of usability sessions
- Final Lighthouse audit
- Feedback from teacher test users

---

For questions or collaboration, contact QA lead or project owner. 