
import os
import sys
import psycopg2
import json

sys.path.append(os.getcwd())

def find_bad_resources():
    try:
        conn = psycopg2.connect(
            dbname="awade",
            user="awade_user",
            password="awade_password",
            host="postgres",
            port="5432"
        )
        cur = conn.cursor()
        
        print("Scannning for bad resources...")
        cur.execute("SELECT lesson_resources_id, ai_generated_content FROM lesson_resources ORDER BY lesson_resources_id;")
        rows = cur.fetchall()
        
        bad_ids = []
        for row in rows:
            res_id = row[0]
            content = row[1]
            
            if content is None:
                # None might be okay if Optional, but let's check
                continue
                
            if isinstance(content, str):
                if not content.strip():
                    print(f"❌ ID {res_id}: Content is empty string (FAIL)")
                    bad_ids.append(res_id)
                    continue
                    
                try:
                    json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"❌ ID {res_id}: JSON Parse Error: {e}")
                    bad_ids.append(res_id)
            else:
                 # It's already an object/dict (if using jsonb driver) or something else
                 pass

        if bad_ids:
            print(f"\nFound {len(bad_ids)} bad records: {bad_ids}")
            print("Run the cleanup command to delete them.")
        else:
            print("\n✅ No bad records found.")
            
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    find_bad_resources()
