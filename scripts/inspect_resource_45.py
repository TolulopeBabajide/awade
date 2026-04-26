
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

def inspect_resource_45():
    try:
        conn = psycopg2.connect(
            dbname="awade",
            user="awade_user",
            password="awade_password",
            host="postgres",
            port="5432"
        )
        cur = conn.cursor()
        
        cur.execute("SELECT lesson_resources_id, ai_generated_content FROM lesson_resources WHERE lesson_resources_id = 45;")
        row = cur.fetchone()
        
        if row:
            res_id = row[0]
            content = row[1]
            print(f"Resource ID: {res_id}")
            # Print plenty of context
            print(f"Content Length: {len(content)}")
            
            try:
                json.loads(content)
                print("✅ JSON parses successfully (As is).")
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
                print(f"Error at position: {e.pos}")
                start = max(0, e.pos - 50)
                end = min(len(content), e.pos + 50)
                print(f"Context: {repr(content[start:end])}")
                
                # Check if repair would have worked
                repaired = repair_json(content)
                if repaired == content:
                    print("⚠️ Repair logic made NO chages to this string used!")
                else:
                    print("ℹ️ Repair logic WOULD modify this string.")
                    
                try:
                    json.loads(repaired)
                    print(f"✅ Repaired JSON parses successfully!")
                except json.JSONDecodeError as e2:
                    print(f"❌ Repaired JSON STILL fails: {e2}")
                
        else:
            print("❌ Resource 45 not found.")
            
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_resource_45()
