"""
PDF Export Service for Awade Lesson Resources

This service handles the generation of professional PDF documents
for lesson resources, including both AI-generated and user-edited content.
"""

import os
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("Warning: WeasyPrint not available. PDF generation will be disabled.")

from sqlalchemy.orm import Session
from ..models import LessonResource, LessonPlan, Topic, CurriculumStructure, Subject, GradeLevel, Curriculum


class PDFService:
    """Service for generating PDF documents from lesson resources."""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
        
    def generate_lesson_resource_pdf(self, lesson_resource: LessonResource, db: Session) -> bytes:
        """
        Generate a professional PDF document from a lesson resource.
        
        Args:
            lesson_resource: The lesson resource to export
            db: Database session
            
        Returns:
            PDF document as bytes
        """
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError("WeasyPrint is not available. Please install it with: pip install weasyprint")
        
        # Get lesson plan and curriculum data
        lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_plan_id == lesson_resource.lesson_plan_id).first()
        if not lesson_plan:
            raise ValueError("Lesson plan not found")
        
        # Get topic and curriculum structure
        topic = db.query(Topic).filter(Topic.topic_id == lesson_plan.topic_id).first()
        if not topic:
            raise ValueError("Topic not found")
        
        curriculum_structure = db.query(CurriculumStructure).filter(
            CurriculumStructure.curriculum_structure_id == topic.curriculum_structure_id
        ).first()
        if not curriculum_structure:
            raise ValueError("Curriculum structure not found")
        
        # Get subject and grade level
        subject = db.query(Subject).filter(Subject.subject_id == curriculum_structure.subject_id).first()
        grade_level = db.query(GradeLevel).filter(GradeLevel.grade_level_id == curriculum_structure.grade_level_id).first()
        curriculum = db.query(Curriculum).filter(Curriculum.curricula_id == curriculum_structure.curricula_id).first()
        
        # Generate HTML content
        html_content = self._generate_html_content(
            lesson_resource=lesson_resource,
            topic=topic,
            subject=subject,
            grade_level=grade_level,
            curriculum=curriculum
        )
        
        # Generate PDF
        html = HTML(string=html_content)
        css = CSS(string=self._get_css_styles())
        
        return html.write_pdf(stylesheets=[css])
    
    def export_to_docx(self, lesson_resource: LessonResource, db: Session) -> bytes:
        """
        Export lesson resource to DOCX format.
        
        Args:
            lesson_resource: The lesson resource to export
            db: Database session
            
        Returns:
            DOCX document as bytes
        """
        # For now, return a simple text representation
        # In a full implementation, you would use python-docx library
        content = self._generate_docx_content(lesson_resource, db)
        return content.encode('utf-8')
    
    def include_ai_and_user_content(self, lesson_resource: LessonResource) -> str:
        """
        Combine AI-generated and user-edited content, prioritizing user edits.
        
        Args:
            lesson_resource: The lesson resource
            
        Returns:
            Combined content as string, with user edits taking precedence
        """
        # If user has edited content, use that as the primary content
        if lesson_resource.user_edited_content:
            primary_content = lesson_resource.user_edited_content
            
            # Add a note about the source if AI content exists
            if lesson_resource.ai_generated_content:
                return f"{primary_content}\n\n---\n\n*Note: This content has been customized by the teacher based on AI-generated suggestions.*"
            else:
                return primary_content
        
        # If no user edits, use AI-generated content
        elif lesson_resource.ai_generated_content:
            return f"{lesson_resource.ai_generated_content}\n\n---\n\n*Note: This is AI-generated content. Teachers are encouraged to review and customize for their specific classroom needs.*"
        
        # Fallback to context input if no other content
        elif lesson_resource.context_input:
            return f"Local Context Information:\n{lesson_resource.context_input}"
        
        # No content available
        else:
            return "No lesson content available."
    
    def format_curriculum_alignment(self, topic: Topic, db: Session) -> str:
        """
        Format curriculum alignment documentation.
        
        Args:
            topic: The topic
            db: Database session
            
        Returns:
            Formatted curriculum alignment text
        """
        alignment_text = []
        
        # Get learning objectives
        for objective in topic.learning_objectives:
            alignment_text.append(f"• {objective.objective}")
        
        alignment_text.append("")
        alignment_text.append("## Topic Contents")
        
        # Get topic contents
        for content in topic.topic_contents:
            alignment_text.append(f"• {content.content_area}")
        
        return "\n".join(alignment_text)
    
    def _get_content_source_info(self, lesson_resource: LessonResource) -> str:
        """
        Generate information about the content source and customization status.
        
        Args:
            lesson_resource: The lesson resource
            
        Returns:
            HTML string with content source information
        """
        info_parts = []
        
        if lesson_resource.user_edited_content:
            info_parts.append("✅ <strong>Teacher Customized:</strong> This content has been reviewed and customized by the teacher for classroom use.")
        elif lesson_resource.ai_generated_content:
            info_parts.append("🤖 <strong>AI Generated:</strong> This content was generated by AI and should be reviewed before classroom use.")
        
        if lesson_resource.context_input:
            info_parts.append("🌍 <strong>Local Context:</strong> Content has been adapted for the specified local context and classroom environment.")
        
        if lesson_resource.status:
            info_parts.append(f"📊 <strong>Status:</strong> {lesson_resource.status.title()}")
        
        if not info_parts:
            info_parts.append("ℹ️ <strong>Note:</strong> Content source information not available.")
        
        return "<br>".join(info_parts)
    
    def _generate_html_content(self, lesson_resource: LessonResource, topic: Topic, 
                             subject: Any, grade_level: Any, curriculum: Any) -> str:
        """Generate HTML content for PDF generation."""
        
        # Get combined content
        combined_content = self.include_ai_and_user_content(lesson_resource)
        
        # Get curriculum alignment
        curriculum_alignment = self.format_curriculum_alignment(topic, lesson_resource.lesson_plan._sa_instance_state.session)
        
        # Format creation date
        created_date = lesson_resource.created_at.strftime("%B %d, %Y") if lesson_resource.created_at else "Unknown"
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Lesson Resource - {topic.topic_title}</title>
        </head>
        <body>
            <div class="container">
                <header class="header">
                    <div class="logo">
                        <h1>Awade</h1>
                        <p>AI-Powered Lesson Resources</p>
                    </div>
                    <div class="metadata">
                        <p><strong>Generated:</strong> {created_date}</p>
                        <p><strong>Resource ID:</strong> {lesson_resource.lesson_resources_id}</p>
                    </div>
                </header>
                
                <div class="content">
                    <div class="curriculum-info">
                        <h2>Curriculum Information</h2>
                        <table class="info-table">
                            <tr>
                                <td><strong>Curriculum:</strong></td>
                                <td>{curriculum.curricula_title if curriculum else 'N/A'}</td>
                            </tr>
                            <tr>
                                <td><strong>Subject:</strong></td>
                                <td>{subject.name if subject else 'N/A'}</td>
                            </tr>
                            <tr>
                                <td><strong>Grade Level:</strong></td>
                                <td>{grade_level.name if grade_level else 'N/A'}</td>
                            </tr>
                            <tr>
                                <td><strong>Topic:</strong></td>
                                <td>{topic.topic_title}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <div class="curriculum-alignment">
                        <h2>Curriculum Alignment</h2>
                        <div class="alignment-content">
                            {curriculum_alignment.replace(chr(10), '<br>')}
                        </div>
                    </div>
                    
                    <div class="lesson-content">
                        <h2>Lesson Resource Content</h2>
                        <div class="content-text">
                            {combined_content.replace(chr(10), '<br>')}
                        </div>
                    </div>
                    
                    <div class="content-source">
                        <h3>Content Information</h3>
                        <div class="source-info">
                            {self._get_content_source_info(lesson_resource)}
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>Generated by Awade - AI-Powered Lesson Resources</p>
                        <p>This resource is designed to be culturally relevant and adaptable to local contexts.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for PDF generation."""
        return """
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "Awade Lesson Resource";
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        
        .container {
            max-width: 100%;
            margin: 0 auto;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 3px solid #f97316;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .logo h1 {
            color: #f97316;
            margin: 0;
            font-size: 28px;
            font-weight: bold;
        }
        
        .logo p {
            margin: 5px 0 0 0;
            color: #666;
            font-size: 14px;
        }
        
        .metadata {
            text-align: right;
            font-size: 12px;
            color: #666;
        }
        
        .metadata p {
            margin: 2px 0;
        }
        
        .content {
            margin-top: 30px;
        }
        
        h2 {
            color: #f97316;
            border-bottom: 2px solid #f97316;
            padding-bottom: 5px;
            margin-top: 30px;
            margin-bottom: 20px;
        }
        
        .info-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        .info-table td {
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
        
        .info-table td:first-child {
            font-weight: bold;
            width: 30%;
        }
        
        .alignment-content {
            background-color: #f9f9f9;
            padding: 15px;
            border-left: 4px solid #f97316;
            margin-bottom: 20px;
        }
        
        .content-text {
            background-color: #fff;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .content-source {
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #28a745;
            margin-bottom: 20px;
        }
        
        .content-source h3 {
            color: #28a745;
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 18px;
        }
        
        .source-info {
            font-size: 14px;
            line-height: 1.5;
            color: #495057;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
        
        .footer p {
            margin: 5px 0;
        }
        
        /* Print-specific styles */
        @media print {
            .header {
                border-bottom-color: #000;
            }
            
            h2 {
                color: #000;
                border-bottom-color: #000;
            }
            
            .alignment-content {
                border-left-color: #000;
            }
        }
        """
    
    def _generate_docx_content(self, lesson_resource: LessonResource, db: Session) -> str:
        """Generate simple text content for DOCX export."""
        # This is a simplified version. In production, use python-docx library
        content = []
        content.append("AWADE LESSON RESOURCE")
        content.append("=" * 50)
        content.append("")
        
        # Get the primary content (prioritizing user edits)
        primary_content = self.include_ai_and_user_content(lesson_resource)
        
        # Add the primary content
        content.append("LESSON CONTENT:")
        content.append("-" * 30)
        content.append(primary_content)
        content.append("")
        
        # Add metadata
        if lesson_resource.context_input:
            content.append("LOCAL CONTEXT:")
            content.append("-" * 30)
            content.append(lesson_resource.context_input)
            content.append("")
        
        content.append("Generated by Awade - AI-Powered Lesson Resources")
        
        return "\n".join(content)


# Create a singleton instance
pdf_service = PDFService() 