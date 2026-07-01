import psycopg2, os, sys
from datetime import datetime, timezone
url = os.environ.get("DATABASE_URL","")
if not url: print("No DATABASE_URL"); sys.exit(1)
conn = psycopg2.connect(url); conn.autocommit = True; cur = conn.cursor()

migs = [
    ("accounts","0001_initial"),
    ("accounts","0002_alter_user_branch_alter_user_role_project_and_more"),
    ("assessment","0001_initial"),
    ("assessment","0002_assessmenttask_project_employee_project"),
    ("assessment","0003_assessmenttemplate_exam_type_and_more"),
]
for app,name in migs:
    cur.execute("SELECT COUNT(*) FROM django_migrations WHERE app=%s AND name=%s",[app,name])
    if cur.fetchone()[0]==0:
        cur.execute("INSERT INTO django_migrations (app,name,applied) VALUES (%s,%s,%s)",[app,name,datetime.now(timezone.utc)])
        print("Inserted: "+app+"."+name)

pwd="pbkdf2_sha256$720000$fix_admin_salt_2024$XlFWe/qtVZ9FND7U/IMtHPNjBTOmrZRET/7DOLxDZKw="
cur.execute("SELECT COUNT(*) FROM accounts_user WHERE username='admin'")
if cur.fetchone()[0]==0:
    cur.execute("INSERT INTO accounts_user (password,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined,role,is_locked) VALUES (%s,true,%s,%s,%s,%s,true,true,%s,%s,false)",
        [pwd,"admin","","","admin@xhzs.com",datetime.now(timezone.utc),"super_admin"])
    print("Created admin user")
else: print("Admin exists")

cur.close(); conn.close()
print("Done!")
