"""
File upload service for handling profile image uploads.
Modified to store images in database as base64 data.
"""

import base64
import io
from typing import Tuple
from fastapi import UploadFile, HTTPException
from PIL import Image

class FileUploadService:
    """Service for handling file uploads with validation and processing."""
    
    # Allowed image types
    ALLOWED_IMAGE_TYPES = {
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg', 
        'image/png': '.png',
        'image/webp': '.webp'
    }
    
    # Maximum file size (5MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    
    # Maximum image dimensions
    MAX_IMAGE_DIMENSIONS = (800, 800)
    
    async def validate_and_process_image(
        self, 
        file: UploadFile
    ) -> Tuple[str, str, str]:
        """
        Validate and process uploaded image file.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Tuple of (base64_image_data, mime_type, file_extension)
            
        Raises:
            HTTPException: If validation fails
        """
        # Check file size
        if file.size and file.size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Check file type
        if file.content_type not in self.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(self.ALLOWED_IMAGE_TYPES.keys())}"
            )
        
        # Read file content
        try:
            content = await file.read()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read uploaded file: {str(e)}"
            )
        
        # Validate and process image
        try:
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large
            if image.width > self.MAX_IMAGE_DIMENSIONS[0] or image.height > self.MAX_IMAGE_DIMENSIONS[1]:
                image.thumbnail(self.MAX_IMAGE_DIMENSIONS, Image.Resampling.LANCZOS)
            
            # Convert to base64
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            processed_content = output.getvalue()
            
            # Convert to base64 string
            base64_data = base64.b64encode(processed_content).decode('utf-8')
            
            # Get file extension
            file_extension = self.ALLOWED_IMAGE_TYPES[file.content_type]
            
            return base64_data, file.content_type, file_extension
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image file: {str(e)}"
            )
    
    async def save_profile_image(
        self, 
        file: UploadFile, 
        user_id: int
    ) -> Tuple[str, str, str]:
        """
        Process profile image for storage in database.
        
        Args:
            file: Uploaded image file
            user_id: ID of the user
            
        Returns:
            Tuple of (base64_data, mime_type, file_extension)
        """
        # Process and validate image
        base64_data, mime_type, file_extension = await self.validate_and_process_image(file)
        
        return base64_data, mime_type, file_extension
    
    async def delete_profile_image(self, image_data: str) -> bool:
        """
        Delete a profile image from database.
        
        Args:
            image_data: Base64 image data
            
        Returns:
            True if deletion was successful (data cleared)
        """
        try:
            # For database storage, we just return True since the data will be cleared
            # when the user profile is updated
            return True
            
        except Exception as e:
            print(f"Error processing profile image deletion: {str(e)}")
            return False
    
    def get_profile_image_data_url(self, base64_data: str, mime_type: str) -> str:
        """
        Get a data URL for a profile image stored as base64.
        
        Args:
            base64_data: Base64 encoded image data
            mime_type: MIME type of the image
            
        Returns:
            Data URL for the image
        """
        return f"data:{mime_type};base64,{base64_data}"

# Global instance
file_upload_service = FileUploadService()
