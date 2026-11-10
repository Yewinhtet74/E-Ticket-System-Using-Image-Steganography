"""
Run before app.py (run_project.bat does this for you).
- Checks that MySQL is running and the login in app.py works.
- If airline_database does not exist yet, creates it from setup_database.sql.
- If it already exists, it is left untouched.
"""
import re
import sys

import pymysql

# Same settings as app.py (lines 20-23). Change both places if yours differ.
HOST, USER, PASSWORD, DB = 'localhost', 'root', 'root', 'airline_database'
REQUIRED_TABLES = {'route', 'plane', 'ticket', 'aes', 'aes2', 'checkincounter', 'adminaccount'}


def main():
    try:
        conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD)
    except pymysql.err.OperationalError as e:
        if e.args and e.args[0] == 1045:
            print(f"  MySQL rejected user '{USER}' with password '{PASSWORD}'.")
            print("  Set the MySQL root password to 'root', or change it in app.py and check_setup.py.")
        else:
            print("  Cannot connect to MySQL on localhost:3306.")
            print("  Install/start MySQL Server 8.0 (Windows: Services -> MySQL80 -> Start).")
        print(f"  Details: {e}")
        return 1

    cur = conn.cursor()
    cur.execute("SHOW DATABASES LIKE %s", (DB,))
    if cur.fetchone():
        cur.execute(f"SHOW TABLES FROM `{DB}`")
        missing = REQUIRED_TABLES - {row[0].lower() for row in cur.fetchall()}
        if missing:
            print(f"  '{DB}' exists but is missing tables: {', '.join(sorted(missing))}")
            return 1
        cur.execute(f"SELECT COUNT(*) FROM `{DB}`.route")
        print(f"  OK - '{DB}' found with {cur.fetchone()[0]} flights.")
        return 0

    print(f"  '{DB}' not found - creating it from setup_database.sql ...")
    with open('setup_database.sql', encoding='utf-8') as f:
        sql = re.sub(r'^\s*--.*$', '', f.read(), flags=re.MULTILINE)
    for statement in sql.split(';'):
        if statement.strip():
            cur.execute(statement)
    conn.commit()
    cur.execute(f"SELECT COUNT(*) FROM `{DB}`.route")
    print(f"  Created '{DB}' with {cur.fetchone()[0]} sample flights. Admin login: admin / admin123")
    return 0


if __name__ == '__main__':
    sys.exit(main())
