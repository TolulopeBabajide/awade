from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from apps.backend.models import CurriculumFramework, CurriculumStandard
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tolulope:awade2025@localhost:5432/awade")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def migrate_curricula_to_framework():
    print("🔄 Migrating flat curricula to hierarchical curriculum_frameworks...")

    # 1. Get all unique countries from curricula
    countries = session.execute(text("SELECT DISTINCT country FROM curricula")).fetchall()
    for (country,) in countries:
        # Create a framework for each country
        framework = CurriculumFramework(
            name=f"{country} National Curriculum",
            country=country,
            description=f"Auto-migrated curriculum for {country}",
            framework_type="NATIONAL",
            is_active=True
        )
        session.add(framework)
        session.commit()
        print(f"✅ Created framework for {country}")

        # 2. For each subject/grade_level, create a standard under this framework
        rows = session.execute(
            text("SELECT subject, grade_level, theme FROM curricula WHERE country = :country"),
            {"country": country}
        ).fetchall()
        for subject, grade_level, theme in rows:
            standard = CurriculumStandard(
                framework_id=framework.framework_id,
                subject=subject,
                grade_level=grade_level,
                standard_code=f"{subject}_{grade_level}".replace(" ", "_"),
                standard_title=f"{subject} {grade_level}",
                standard_description=theme or "",
                is_core=True
            )
            session.add(standard)
        session.commit()
        print(f"✅ Migrated standards for {country}")

    print("🎉 Migration complete!")

if __name__ == "__main__":
    migrate_curricula_to_framework() 