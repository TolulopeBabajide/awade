"""
PDF Export Service for Awade Lesson Resources

This service handles the generation of professional PDF documents
for lesson resources, including both AI-generated and user-edited content.
"""

import logging
import os
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False
    logger.warning("WeasyPrint not available — PDF generation will be disabled.")

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
            curriculum=curriculum,
            db=db,
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
                             subject: Any, grade_level: Any, curriculum: Any,
                             db: Session) -> str:
        """Generate HTML content for PDF generation."""

        # Get combined content
        combined_content = self.include_ai_and_user_content(lesson_resource)

        # Get curriculum alignment
        curriculum_alignment = self.format_curriculum_alignment(topic, db)
        
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


    # ── Parent Guide PDF ──────────────────────────────────────────────────────

    def generate_guide_pdf(self, content: dict, meta: dict) -> bytes:
        """
        Generate a printable PDF from an AI-generated parent guide.

        Args:
            content: Parsed dict matching ParentGuideAIContent schema
            meta:    Dict with guide_id, topic_title, subject_name

        Returns:
            PDF document as bytes
        """
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError(
                "WeasyPrint is not available. "
                "Install with: pip install weasyprint"
            )
        html_content = self._generate_guide_html(content, meta)
        html = HTML(string=html_content)
        css = CSS(string=self._get_guide_css_styles())
        return html.write_pdf(stylesheets=[css])

    def _generate_guide_html(self, content: dict, meta: dict) -> str:
        """Generate HTML for a parent guide PDF."""
        header = content.get("topic_header", {})
        explanation = content.get("simple_explanation", {})
        activity = content.get("home_activity", {})
        starters = content.get("conversation_starters", [])
        mistakes = content.get("common_mistakes", [])
        curriculum_ctx = content.get("curriculum_context") or {}
        tips = content.get("encouragement_tips", [])

        topic = header.get("topic", meta.get("topic_title", "Guide"))
        subject = header.get("subject", meta.get("subject_name", ""))
        grade = header.get("grade_level", "")
        country = header.get("country", "")
        curriculum = header.get("curriculum", "")

        # Materials list
        materials_html = ""
        if activity.get("materials_needed"):
            items = "".join(
                f"<li>{self._h(m)}</li>" for m in activity["materials_needed"]
            )
            materials_html = f"<p class='label'>You'll need:</p><ul>{items}</ul>"

        # Activity steps
        steps_html = ""
        if activity.get("steps"):
            items = "".join(
                f"<li>{self._h(s)}</li>" for s in activity["steps"]
            )
            steps_html = f"<ol>{items}</ol>"

        # Conversation starters
        starters_html = "".join(
            f'<div class="quote">"{self._h(q)}"</div>' for q in starters
        )

        # Common mistakes
        mistakes_html = ""
        for m in mistakes:
            mistakes_html += f"""
            <div class="mistake-card">
                <p class="mistake-title">{self._h(m.get('mistake', ''))}</p>
                <p class="mistake-reason">{self._h(m.get('why_it_happens', ''))}</p>
                <div class="how-to-help">
                    <strong>How to help:</strong> {self._h(m.get('how_to_help', ''))}
                </div>
            </div>"""

        # Curriculum context
        ctx_html = ""
        ctx_rows = [
            ("Before this topic", curriculum_ctx.get("what_came_before")),
            ("After this topic", curriculum_ctx.get("what_comes_next")),
            ("Time in school", curriculum_ctx.get("how_long_in_school")),
        ]
        for label, val in ctx_rows:
            if val:
                ctx_html += f"""
                <div class="ctx-card">
                    <p class="ctx-label">{label}</p>
                    <p class="ctx-value">{self._h(val)}</p>
                </div>"""

        # Encouragement tips
        tips_html = "".join(
            f'<div class="tip">{self._h(t)}</div>' for t in (tips or [])
        )

        from datetime import date as _date
        today = _date.today().strftime("%B %d, %Y")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Awade Guide — {self._h(topic)}</title>
</head>
<body>
<div class="page">

  <!-- Header -->
  <header class="page-header">
    <div class="brand">
      <span class="brand-name">awade</span>
      <span class="brand-tagline">How to Help Your Child</span>
    </div>
    <div class="guide-meta">
      <span>{self._h(subject)}</span>
      {'<span class="sep">·</span><span>' + self._h(grade) + '</span>' if grade else ''}
      {'<span class="sep">·</span><span>' + self._h(country) + '</span>' if country else ''}
    </div>
  </header>

  <!-- Topic title -->
  <h1 class="topic-title">{self._h(topic)}</h1>
  {'<p class="curriculum-label">' + self._h(curriculum) + '</p>' if curriculum else ''}

  <!-- What is this topic? -->
  <section>
    <h2>💡 What is this topic about?</h2>
    <p>{self._h(explanation.get('what_it_is', ''))}</p>
    {'<p class="why-matters">' + self._h(explanation.get('why_it_matters', '')) + '</p>'
      if explanation.get('why_it_matters') else ''}
  </section>

  <!-- Home Activity -->
  <section>
    <h2>🏠 {self._h(activity.get('title', 'Home Activity'))}</h2>
    <p class="activity-subtitle">Home activity · 15–30 minutes</p>
    <p>{self._h(activity.get('description', ''))}</p>
    {materials_html}
    {steps_html}
    {'<div class="look-for"><strong>What to look for:</strong> '
      + self._h(activity.get('what_to_look_for', '')) + '</div>'
      if activity.get('what_to_look_for') else ''}
  </section>

  <!-- Conversation starters -->
  {'<section><h2>💬 Conversation starters</h2>' + starters_html + '</section>'
    if starters else ''}

  <!-- Common mistakes -->
  {'<section><h2>⚠️ Common mistakes to watch for</h2>' + mistakes_html + '</section>'
    if mistakes else ''}

  <!-- Curriculum context -->
  {'<section><h2>📚 Where this fits in the curriculum</h2><div class="ctx-grid">'
    + ctx_html + '</div></section>'
    if ctx_html else ''}

  <!-- Encouragement tips -->
  {'<section><h2>❤️ Encouragement tips</h2>' + tips_html + '</section>'
    if tips else ''}

  <!-- Footer -->
  <footer>
    <p>Generated by Awade · awade.app · {today}</p>
    <p style="color:#999;font-size:10pt;">
      This guide is AI-generated. Review and adapt for your child's needs.
    </p>
  </footer>

</div>
</body>
</html>"""

    @staticmethod
    def _h(text: str) -> str:
        """Escape HTML special characters."""
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        return (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
        )

    def _get_guide_css_styles(self) -> str:
        """CSS styles for parent guide PDFs."""
        return """
@page {
    size: A4;
    margin: 2cm 2cm 2.5cm 2cm;
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #999;
    }
}

body {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1a1a2e;
    margin: 0;
    padding: 0;
}

.page { max-width: 100%; }

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    border-bottom: 3px solid #6c63ff;
    padding-bottom: 10px;
    margin-bottom: 8px;
}

.brand-name {
    font-size: 22pt;
    font-weight: 800;
    color: #6c63ff;
    letter-spacing: -1px;
}

.brand-tagline {
    display: block;
    font-size: 9pt;
    color: #888;
    margin-top: 2px;
}

.guide-meta {
    font-size: 10pt;
    color: #555;
    text-align: right;
}

.sep { margin: 0 6px; color: #bbb; }

.topic-title {
    font-size: 22pt;
    font-weight: 700;
    color: #1a1a2e;
    margin: 14px 0 4px 0;
    line-height: 1.25;
}

.curriculum-label {
    font-size: 10pt;
    color: #888;
    margin: 0 0 18px 0;
}

section { margin-bottom: 22px; }

h2 {
    font-size: 13pt;
    font-weight: 700;
    color: #3d3d8f;
    border-left: 4px solid #6c63ff;
    padding-left: 10px;
    margin: 0 0 10px 0;
}

p { margin: 0 0 8px 0; }

.why-matters {
    font-style: italic;
    color: #555;
    font-size: 10.5pt;
}

.activity-subtitle {
    font-size: 9.5pt;
    color: #888;
    margin: -6px 0 8px 0;
}

.label { font-weight: 600; color: #444; margin-bottom: 4px; }

ul, ol { margin: 4px 0 10px 0; padding-left: 22px; }
li { margin-bottom: 4px; }

.look-for {
    background: #f0fdf4;
    border-left: 3px solid #22c55e;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 10.5pt;
    margin-top: 10px;
}

.quote {
    background: #eff6ff;
    border-left: 3px solid #3b82f6;
    padding: 8px 12px;
    border-radius: 4px;
    font-style: italic;
    color: #1e3a5f;
    margin-bottom: 8px;
    font-size: 10.5pt;
}

.mistake-card {
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 10px;
}

.mistake-title {
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 3px;
}

.mistake-reason {
    font-size: 10pt;
    color: #666;
    margin-bottom: 6px;
}

.how-to-help {
    background: #fffbeb;
    border-left: 3px solid #f59e0b;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 10.5pt;
}

.ctx-grid {
    display: flex;
    gap: 10px;
}

.ctx-card {
    flex: 1;
    background: #f8f9fb;
    border-radius: 6px;
    padding: 10px 12px;
}

.ctx-label {
    font-size: 9pt;
    font-weight: 700;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.ctx-value { font-size: 10.5pt; color: #333; margin: 0; }

.tip {
    background: #fff1f2;
    border-left: 3px solid #f43f5e;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 10.5pt;
    margin-bottom: 8px;
}

footer {
    margin-top: 30px;
    padding-top: 12px;
    border-top: 1px solid #e5e7eb;
    text-align: center;
    font-size: 9.5pt;
    color: #666;
}
"""


# Create a singleton instance
pdf_service = PDFService() 