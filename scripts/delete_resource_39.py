
import os
import sys
import psycopg2

sys.path.append(os.getcwd())

def delete_invalid_resource():
    try:
        conn = psycopg2.connect(
            dbname="awade",
            user="awade_user",
            password="awade_password",
            host="postgres",
            port="5432"
        )
        cur = conn.cursor()
        
        # Delete corrupted record
        print("Deleting corrupted Resource ID 39...")
        cur.execute("DELETE FROM lesson_resources WHERE lesson_resources_id = 39;")
        
        conn.commit()
        print(f"✅ Deleted {cur.rowcount} record(s).")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error deleting record: {e}")

if __name__ == "__main__":
    delete_invalid_resource()
