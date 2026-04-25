
import os
import sys
import psycopg2
from pydantic import BaseModel, Json, ValidationError
from typing import Optional

sys.path.append(os.getcwd())

class LessonResourceResponse(BaseModel):
    ai_generated_content: Optional[Json] = None

def test_pydantic_parsing():
    try:
        conn = psycopg2.connect(
            dbname="awade",
            user="awade_user",
            password="awade_password",
            host="postgres",
            port="5432"
        )
        cur = conn.cursor()
        
        cur.execute("SELECT ai_generated_content FROM lesson_resources WHERE lesson_resources_id = 40;")
        row = cur.fetchone()
        
        if row:
            content = row[0]
            print(f"Testing Pydantic parsing for content of length {len(content)}...")
            try:
                # Simulate what happens in the route
                model = LessonResourceResponse(ai_generated_content=content)
                print("✅ Pydantic Validated Successfully!")
                print(f"Parsed type: {type(model.ai_generated_content)}")
            except ValidationError as e:
                print(f"❌ Pydantic Validation Error: {e}")
                print(f"Input repr: {repr(content[:100])}...")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_pydantic_parsing()
