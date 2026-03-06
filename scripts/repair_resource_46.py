
import os
import sys
import psycopg2
import json
import re

sys.path.append(os.getcwd())

def clean_and_repair(content):
    if not content: return ""
    clean_content = content.replace("```json", "").replace("```", "").strip()
    if "{" in clean_content:
        match = re.search(r'(\{.*\})', clean_content, re.DOTALL)
        if match:
            clean_content = match.group(1)
            
    # Repair
    clean_content = re.sub(r',\s*}', '}', clean_content)
    clean_content = re.sub(r',\s*\]', ']', clean_content)
    return clean_content

def repair_resource_46():
    try:
        conn = psycopg2.connect(
            dbname="awade",
            user="awade_user",
            password="awade_password",
            host="postgres",
            port="5432"
        )
        cur = conn.cursor()
        
        # Fetch
        cur.execute("SELECT ai_generated_content FROM lesson_resources WHERE lesson_resources_id = 46;")
        row = cur.fetchone()
        
        if row:
            content = row[0]
            print("Found Resource 46.")
            
            # Repair
            repaired = clean_and_repair(content)
            
            # Validate
            try:
                json.loads(repaired)
                print("✅ Repaired content is valid JSON.")
                
                # Update DB
                cur.execute(
                    "UPDATE lesson_resources SET ai_generated_content = %s, status = 'generated' WHERE lesson_resources_id = 46;",
                    (repaired,)
                )
                conn.commit()
                print("✅ Successfully updated Resource 46 in DB.")
                
            except json.JSONDecodeError as e:
                print(f"❌ Repaired content is STILL invalid: {e}")
        else:
            print("❌ Resource 46 not found.")
            
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    repair_resource_46()
