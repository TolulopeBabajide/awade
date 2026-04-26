
import os
import sys
import psycopg2
import json

sys.path.append(os.getcwd())

def validate_all_resources():
    try:
        conn = psycopg2.connect(
            dbname="awade",
            user="awade_user",
            password="awade_password",
            host="postgres",
            port="5432"
        )
        cur = conn.cursor()
        
        cur.execute("SELECT lesson_resources_id, ai_generated_content FROM lesson_resources WHERE ai_generated_content IS NOT NULL;")
        rows = cur.fetchall()
        
        print(f"Validating {len(rows)} records...")
        
        invalid_ids = []
        for row in rows:
            res_id = row[0]
            content = row[1]
            
            if not isinstance(content, str):
                continue
                
            try:
                json.loads(content)
            except Exception as e:
                print(f"❌ Invalid JSON in ID {res_id}: {e}")
                # Print a snippet to see what's wrong
                print(f"   Snippet: {repr(content[:100])}...")
                print(f"   End: {repr(content[-100:])}...")
                invalid_ids.append(res_id)
        
        if invalid_ids:
            print(f"⚠️ Found {len(invalid_ids)} invalid records: {invalid_ids}")
            # Optional: Clear them?
            # for i in invalid_ids:
            #     cur.execute("UPDATE lesson_resources SET ai_generated_content = NULL, status='failed' WHERE lesson_resources_id = %s", (i,))
            # conn.commit()
        else:
            print("✅ All record contents are valid JSON.")
            
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    validate_all_resources()
