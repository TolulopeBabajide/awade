
import os
import sys
import psycopg2
import re

# Add root path if needed
sys.path.append(os.getcwd())

def clean_json_content():
    try:
        conn = psycopg2.connect(
            dbname="awade",
            user="awade_user",
            password="awade_password",
            host="postgres",
            port="5432"
        )
        cur = conn.cursor()
        
        # Fetch all resources with content
        cur.execute("SELECT lesson_resources_id, ai_generated_content FROM lesson_resources WHERE ai_generated_content IS NOT NULL;")
        rows = cur.fetchall()
        
        print(f"Checking {len(rows)} rows for markdown formatting...")
        
        fixed_count = 0
        for row in rows:
            res_id = row[0]
            content = row[1]
            
            if not isinstance(content, str):
                continue

            original_content = content
            
            # Logic to strip markdown
            # Remove start
            if content.strip().startswith("```"):
                content = re.sub(r"^\s*```[a-zA-Z]*\s*", "", content)
            
            # Remove end
            if content.strip().endswith("```"):
                content = re.sub(r"\s*```\s*$", "", content)
                
            if content != original_content:
                print(f"Fixing Resource ID {res_id}...")
                cur.execute(
                    "UPDATE lesson_resources SET ai_generated_content = %s WHERE lesson_resources_id = %s",
                    (content, res_id)
                )
                fixed_count += 1
        
        conn.commit()
        print(f"✅ Successfully fixed {fixed_count} records.")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error fixing DB: {e}")

if __name__ == "__main__":
    clean_json_content()
