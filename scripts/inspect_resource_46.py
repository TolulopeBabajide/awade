
import os
import sys
import psycopg2
import json
import re

sys.path.append(os.getcwd())

def inspect_resource_46():
    try:
        conn = psycopg2.connect(
            dbname="awade",
            user="awade_user",
            password="awade_password",
            host="postgres",
            port="5432"
        )
        cur = conn.cursor()
        
        cur.execute("SELECT lesson_resources_id, ai_generated_content FROM lesson_resources WHERE lesson_resources_id = 46;")
        row = cur.fetchone()
        
        if row:
            res_id = row[0]
            content = row[1]
            print(f"Resource ID: {res_id}")
            print(f"Content Length: {len(content)}")
            
            # Print the context around position 9646 (from screenshot)
            # and 11307
            
            positions = [9646, 11307]
            for pos in positions:
                start = max(0, pos - 100)
                end = min(len(content), pos + 100)
                print(f"\n--- Context around position {pos} ---")
                print(repr(content[start:end]))
                print("-" * 30)
            
            try:
                json.loads(content)
                print("✅ JSON parses successfully (As is).")
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
                print(f"Error at position: {e.pos}")
                
        else:
            print("❌ Resource 46 not found.")
            
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_resource_46()
