# TODO

## Backend API

### Completed ✅
- [x] **enhance-lesson-plan-endpoint-curriculum-fetch**: Enhance POST /api/lesson-plans/generate endpoint to fetch learning objectives and contents for the provided topic from the curriculum DB and include them in the response (without passing to AI).
- [x] **update-schemas-lesson-plan-alignment**: Update schemas to align with current implementation (user_id instead of author_id, optional duration_minutes, curriculum fields).
- [x] **remove-schema-router-redundancy**: Remove redundant schemas and consolidate router logic with helper functions to reduce code duplication.
- [x] **add-comprehensive-error-handling**: Add comprehensive error handling for curriculum mapping failures, database errors, validation errors, and AI service failures.
- [x] **implement-comprehensive-lesson-resource-generation**: Implement GPT service for comprehensive lesson resource generation with curriculum alignment, local context integration, and structured JSON output including title header, learning objectives, lesson content, assessment, activities, key takeaways, related resources/projects, and references.

### In Progress 🔄
- [ ] **update-api-docs-lesson-plan-curriculum-fields**: Update API documentation and response schema to reflect the new fields for objectives and contents in the lesson plan generation response.

### Pending ⏳
- [ ] Implement proper authentication and authorization for lesson plan endpoints
- [ ] Add validation for curriculum data consistency
- [ ] Create unit tests for curriculum mapping functionality
- [ ] Add logging for curriculum data fetching operations
- [x] **fix-resource-generation-endpoint**: Fix resource generation endpoint to properly handle AI service integration with curriculum data extraction and local context support.
- [ ] Add proper error handling for missing topic relationships
- [ ] Consider adding duration_minutes back to LessonPlanCreate schema if needed by frontend
- [ ] Add structured logging instead of print statements
- [ ] Implement retry logic for database operations
- [ ] Add metrics and monitoring for error rates

## Frontend

### Completed ✅
- [x] **integrate-lesson-plan-generation**: Integrate /api/lesson-plans/generate endpoint with UI
- [x] **update-lesson-plan-detail-page**: Update LessonPlanDetailPage to display curriculum data and allow context input
- [x] **add-navigation-flow**: Implement navigation from dashboard to lesson plan detail page

### Pending ⏳
- [ ] Add curriculum data display in lesson plan creation form
- [ ] Implement error handling for curriculum mapping failures in UI
- [ ] Add loading states for curriculum data fetching
- [ ] Add user-friendly error messages for different error types
- [ ] Add authentication context for user_id
- [ ] Implement proper form validation with better UX
- [ ] Add success/error notifications instead of alerts
- [ ] Add loading spinners and better loading states
- [ ] Implement proper error boundaries

## Documentation

### Pending ⏳
- [ ] Update API documentation with new curriculum fields
- [ ] Create user guide for curriculum mapping feature
- [ ] Document the curriculum data flow and relationships
- [ ] Document error handling patterns and error codes
- [ ] Create frontend integration guide 