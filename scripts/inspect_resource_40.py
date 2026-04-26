
import os
import sys
import psycopg2
import json

sys.path.append(os.getcwd())

def inspect_resource_40():
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
            print(f"Content Length: {len(content)}")
            print(f"Starts with: {repr(content[:50])}")
            print(f"Ends with: {repr(content[-50:])}")
            
            try:
                if isinstance(content, str):
                    json.loads(content)
                    print("✅ JSON parses successfully with python json.loads")
                else:
                    print("⚠️ Content is not a string (maybe dict?)")
            except Exception as e:
                print(f"❌ JSON Parse Error: {e}")
        else:
            print("❌ Resource 40 not found.")
            
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_resource_40()
