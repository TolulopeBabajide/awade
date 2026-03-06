
import os
import sys
import psycopg2
import json

sys.path.append(os.getcwd())

def inspect_latest_resource():
    try:
        conn = psycopg2.connect(
            dbname="awade",
            user="awade_user",
            password="awade_password",
            host="postgres",
            port="5432"
        )
        cur = conn.cursor()
        
        # Get the very latest resource
        cur.execute("SELECT lesson_resources_id, ai_generated_content FROM lesson_resources ORDER BY lesson_resources_id DESC LIMIT 1;")
        row = cur.fetchone()
        
        if row:
            res_id = row[0]
            content = row[1]
            print(f"Latest Resource ID: {res_id}")
            print(f"Content Length: {len(content)}")
            
            # Try to parse
            try:
                json.loads(content)
                print("✅ JSON parses successfully.")
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
                print(f"Error at position: {e.pos}")
                # Print context around the error
                start = max(0, e.pos - 50)
                end = min(len(content), e.pos + 50)
                print(f"Context: {repr(content[start:end])}")
                
        else:
            print("❌ No resources found.")
            
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_latest_resource()
