# TODO

## Backend API

### Completed ✅
- [x] **enhance-lesson-plan-endpoint-curriculum-fetch**: Enhance POST /api/lesson-plans/generate endpoint to fetch learning objectives and contents for the provided topic from the curriculum DB and include them in the response (without passing to AI).
- [x] **update-schemas-lesson-plan-alignment**: Update schemas to align with current implementation (user_id instead of author_id, optional duration_minutes, curriculum fields).
- [x] **remove-schema-router-redundancy**: Remove redundant schemas and consolidate router logic with helper functions to reduce code duplication.

### In Progress 🔄
- [ ] **update-api-docs-lesson-plan-curriculum-fields**: Update API documentation and response schema to reflect the new fields for objectives and contents in the lesson plan generation response.

### Pending ⏳
- [ ] Add comprehensive error handling for curriculum mapping failures
- [ ] Implement proper authentication and authorization for lesson plan endpoints
- [ ] Add validation for curriculum data consistency
- [ ] Create unit tests for curriculum mapping functionality
- [ ] Add logging for curriculum data fetching operations
- [ ] Fix resource generation endpoint to properly handle AI service integration
- [ ] Add proper error handling for missing topic relationships
- [ ] Consider adding duration_minutes back to LessonPlanCreate schema if needed by frontend

## Frontend

### Pending ⏳
- [ ] Update lesson plan creation form to display fetched curriculum objectives and contents
- [ ] Add curriculum data display in lesson plan detail view
- [ ] Implement error handling for curriculum mapping failures in UI
- [ ] Add loading states for curriculum data fetching

## Documentation

### Pending ⏳
- [ ] Update API documentation with new curriculum fields
- [ ] Create user guide for curriculum mapping feature
- [ ] Document the curriculum data flow and relationships 