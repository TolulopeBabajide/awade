from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Awade API",
    description="AI-powered educator support platform for African teachers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LessonPlanRequest(BaseModel):
    subject: str
    grade: str
    objectives: List[str]
    duration: Optional[int] = 45
    language: Optional[str] = "en"

class LessonPlan(BaseModel):
    id: str
    title: str
    subject: str
    grade: str
    objectives: List[str]
    activities: List[str]
    materials: List[str]
    assessment: str
    rationale: str
    created_at: str

class TrainingModule(BaseModel):
    id: str
    title: str
    description: str
    duration: int
    category: str
    language: str
    is_offline: bool

# Mock data for MVP
MOCK_LESSON_PLANS = [
    LessonPlan(
        id="lp_001",
        title="Introduction to Fractions",
        subject="Mathematics",
        grade="Grade 4",
        objectives=["Understand basic fractions", "Identify numerator and denominator"],
        activities=["Visual fraction representation", "Group activities with fraction cards"],
        materials=["Fraction cards", "Whiteboard", "Colored markers"],
        assessment="Students create their own fraction examples",
        rationale="Builds foundational understanding through visual and hands-on learning",
        created_at="2025-01-15T10:00:00Z"
    )
]

MOCK_TRAINING_MODULES = [
    TrainingModule(
        id="tm_001",
        title="Effective Classroom Management",
        description="Learn strategies for maintaining an engaging and organized classroom environment",
        duration=15,
        category="Classroom Management",
        language="en",
        is_offline=True
    ),
    TrainingModule(
        id="tm_002",
        title="Using Technology in Teaching",
        description="Integrate digital tools effectively in your lessons",
        duration=20,
        category="Technology Integration",
        language="en",
        is_offline=False
    )
]

@app.get("/")
async def root():
    return {"message": "Welcome to Awade API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "awade-api"}

@app.post("/api/lesson-plans/generate", response_model=LessonPlan)
async def generate_lesson_plan(request: LessonPlanRequest):
    """
    Generate an AI-powered lesson plan based on subject, grade, and objectives.
    """
    # Mock AI generation - in production, this would call OpenAI API
    lesson_plan = LessonPlan(
        id=f"lp_{len(MOCK_LESSON_PLANS) + 1:03d}",
        title=f"{request.subject} Lesson Plan",
        subject=request.subject,
        grade=request.grade,
        objectives=request.objectives,
        activities=[
            "Introduction activity (5 minutes)",
            "Main lesson content (30 minutes)",
            "Assessment and reflection (10 minutes)"
        ],
        materials=["Whiteboard", "Markers", "Student worksheets"],
        assessment="Formative assessment through observation and student responses",
        rationale="This lesson plan follows best practices for active learning and student engagement",
        created_at="2025-01-15T10:00:00Z"
    )
    
    MOCK_LESSON_PLANS.append(lesson_plan)
    return lesson_plan

@app.get("/api/lesson-plans", response_model=List[LessonPlan])
async def get_lesson_plans():
    """
    Retrieve all saved lesson plans.
    """
    return MOCK_LESSON_PLANS

@app.get("/api/lesson-plans/{plan_id}", response_model=LessonPlan)
async def get_lesson_plan(plan_id: str):
    """
    Retrieve a specific lesson plan by ID.
    """
    for plan in MOCK_LESSON_PLANS:
        if plan.id == plan_id:
            return plan
    raise HTTPException(status_code=404, detail="Lesson plan not found")

@app.get("/api/training-modules", response_model=List[TrainingModule])
async def get_training_modules():
    """
    Retrieve all available training modules.
    """
    return MOCK_TRAINING_MODULES

@app.get("/api/training-modules/{module_id}", response_model=TrainingModule)
async def get_training_module(module_id: str):
    """
    Retrieve a specific training module by ID.
    """
    for module in MOCK_TRAINING_MODULES:
        if module.id == module_id:
            return module
    raise HTTPException(status_code=404, detail="Training module not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 