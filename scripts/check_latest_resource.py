
import os
import sys
import psycopg2
import json

# Add root path if needed
sys.path.append(os.getcwd())

def check_latest_resource():
    try:
        # Default credentials from docker-compose
        conn = psycopg2.connect(
            dbname="awade",
            user="awade_user",
            password="awade_password",
            host="postgres",
            port="5432"
        )
        cur = conn.cursor()
        
        # Get latest resource
        # Columns: lesson_resources_id, ai_generated_content, status
        cur.execute("SELECT lesson_resources_id, ai_generated_content, status FROM lesson_resources ORDER BY created_at DESC LIMIT 1;")
        row = cur.fetchone()
        
        if row:
            print(f"✅ Latest Resource ID: {row[0]}")
            print(f"Status: {row[2]}")
            print("Content Snippet (First 500 chars):")
            content = row[1]
            if content:
                try:
                    # Attempt to parse json string if it's stored as string
                    if isinstance(content, str):
                        content_json = json.loads(content)
                        print(json.dumps(content_json, indent=2)[:500])
                    else:
                        print(json.dumps(content, indent=2)[:500])
                except Exception as e:
                    print(f"Raw content: {content[:500]}")
            else:
                print("❌ Content is EMPTY/NULL")
        else:
            print("⚠️ No resources found.")
            
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error connecting to DB: {e}")

if __name__ == "__main__":
    check_latest_resource()
