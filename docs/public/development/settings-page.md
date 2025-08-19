# Settings Page - User Profile Management

## Overview

The Settings page provides comprehensive user profile management capabilities for the AWADE platform, including profile image uploads, personal information editing, and security settings.

## Features

### 1. Profile Management
- **Profile Image Upload**: Users can upload profile pictures with automatic resizing and optimization
- **Personal Information**: Edit first name, last name, country, city, phone, and bio
- **Education Information**: Display educational background and certifications
- **Real-time Editing**: Inline editing with save/cancel functionality

### 2. Security Settings
- **Login Details**: View and edit username/password
- **Two-Factor Authentication**: Toggle 2FA on/off
- **Login Activity**: Monitor active sessions across devices
- **Session Management**: Sign out from all sessions

### 3. File Upload System
- **Image Validation**: Supports JPEG, PNG, and WebP formats
- **Size Limits**: Maximum 5MB file size
- **Auto-optimization**: Automatic resizing to 800x800px maximum
- **Secure Storage**: User-specific upload directories

## Technical Implementation

### Backend Components

#### Models
```python
class User(Base):
    # ... existing fields ...
    profile_image_url = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    bio = Column(Text, nullable=True)
```

#### File Upload Service
- **Location**: `apps/backend/services/file_upload_service.py`
- **Features**: Image validation, processing, and storage
- **Security**: File type validation, size limits, secure file paths

#### API Endpoints
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/profile/upload-image` - Upload profile image
- `DELETE /api/users/profile/delete-image` - Delete profile image
- `GET /api/users/profile` - Get current user profile

### Frontend Components

#### Settings Page
- **Location**: `apps/frontend/src/pages/SettingsPage.tsx`
- **Features**: Tabbed interface, form validation, image preview
- **State Management**: Local state for editing, form validation

#### API Integration
- **Service**: `apps/frontend/src/services/api.ts`
- **Methods**: `updateProfile()`, `uploadProfileImage()`, `deleteProfileImage()`

## Database Schema

### New Fields Added
```sql
ALTER TABLE users ADD COLUMN profile_image_url VARCHAR(500);
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
ALTER TABLE users ADD COLUMN bio TEXT;
```

### Migration File
- **Location**: `apps/backend/migrations/006_add_profile_fields.py`
- **Dependencies**: Requires previous migration `005_add_user_id_to_lesson_plans`

## File Storage

### Directory Structure
```
uploads/
└── profile_images/
    └── {user_id}/
        └── {uuid}.jpg
```

### Security Features
- User-specific directories prevent cross-user access
- UUID-based filenames prevent enumeration attacks
- File type and size validation
- Automatic cleanup of old images

## Usage Examples

### Upload Profile Image
```typescript
const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
  const file = event.target.files?.[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiService.uploadProfileImage(formData);
  if (response.data) {
    // Refresh profile data
    await loadUserProfile();
  }
};
```

### Update Profile Information
```typescript
const handleSaveProfile = async () => {
  try {
    const response = await apiService.updateProfile(editForm);
    if (response.data) {
      setProfileData(response.data);
      setIsEditing(false);
    }
  } catch (error) {
    console.error('Error updating profile:', error);
  }
};
```

## Styling and UI

### Design System
- **Colors**: Uses existing AWADE color palette (primary, accent, background)
- **Components**: Consistent with existing design patterns
- **Responsive**: Mobile-first design with desktop enhancements

### Key UI Elements
- **Profile Image**: Circular design with upload/delete overlays
- **Form Fields**: Consistent input styling with focus states
- **Tabs**: Horizontal navigation between profile, security, and language
- **Buttons**: Primary actions use accent color, secondary actions use gray

## Error Handling

### Validation Errors
- File size and type validation
- Form field validation
- API error responses

### User Feedback
- Loading states during operations
- Success/error notifications
- Form validation messages

## Security Considerations

### File Upload Security
- File type whitelisting
- Size limits enforced
- Secure file paths
- User isolation

### API Security
- Authentication required for all endpoints
- User can only modify their own profile
- Admin users can modify any profile

## Future Enhancements

### Planned Features
- **Profile Image Cropping**: Client-side image editing
- **Multiple Image Support**: Gallery of profile images
- **Advanced Security**: Password change, email verification
- **Notification Preferences**: Email and push notification settings

### Technical Improvements
- **Image CDN**: Cloud storage for better performance
- **Caching**: Profile data caching for faster loading
- **Real-time Updates**: WebSocket integration for live updates

## Testing

### Backend Tests
- File upload validation
- API endpoint security
- Database operations

### Frontend Tests
- Component rendering
- Form validation
- API integration
- User interactions

## Deployment

### Requirements
- **Python Dependencies**: Pillow library for image processing
- **File Permissions**: Write access to uploads directory
- **Storage**: Adequate disk space for profile images

### Environment Variables
```bash
# Optional: Customize upload settings
UPLOAD_MAX_SIZE=5242880  # 5MB in bytes
UPLOAD_MAX_DIMENSIONS=800  # Maximum image dimensions
```

## Troubleshooting

### Common Issues
1. **Image Upload Fails**: Check file size and format
2. **Profile Not Saving**: Verify API authentication
3. **Images Not Displaying**: Check file permissions and static file serving

### Debug Steps
1. Check browser console for errors
2. Verify API endpoint responses
3. Check file system permissions
4. Validate database schema

## Contributing

When contributing to the settings page:

1. Follow existing code patterns and styling
2. Add appropriate error handling
3. Include unit tests for new functionality
4. Update documentation for API changes
5. Consider security implications of new features
