
import os
import sys
import psycopg2
import json
import re

sys.path.append(os.getcwd())

def repair_json(json_str):
    if not json_str: return json_str
    # Replicating the logic from gpt_service.py
    js = re.sub(r',\s*}', '}', json_str)
    js = re.sub(r',\s*\]', ']', js)
    return js

def inspect_resource_51():
    try:
        conn = psycopg2.connect(
            dbname="awade",
            user="awade_user",
            password="awade_password",
            host="postgres",
            port="5432"
        )
        cur = conn.cursor()
        
        cur.execute("SELECT lesson_resources_id, ai_generated_content FROM lesson_resources WHERE lesson_resources_id = 51;")
        row = cur.fetchone()
        
        if row:
            res_id = row[0]
            content = row[1]
            print(f"Resource ID: {res_id}")
            print(f"Content Preview (End): {repr(content[-200:])}")
            
            try:
                json.loads(content)
                print("✅ JSON parses successfully (As is).")
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
                
                # Try repair
                repaired = repair_json(content)
                try:
                    json.loads(repaired)
                    print(f"✅ Repaired JSON parses successfully!")
                except json.JSONDecodeError as e2:
                    print(f"❌ Repaired JSON STILL fails: {e2}")
                    print("Debug Context around failure:")
                    start = max(0, e2.pos - 50)
                    end = min(len(repaired), e2.pos + 50)
                    print(f"Context: {repr(repaired[start:end])}")
                
        else:
            print("❌ Resource 51 not found.")
            
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_resource_51()
