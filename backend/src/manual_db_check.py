#!/usr/bin/env python3
"""
Manual PostgreSQL database checks for Render shell.
Simple SQL commands to verify database schema manually.
"""

import os
import sys

def print_manual_commands():
    """Print PostgreSQL commands that can be run manually."""
    
    print("=" * 70)
    print("MANUAL POSTGRESQL DATABASE VERIFICATION COMMANDS")
    print("=" * 70)
    print("\nRun these commands in your Render shell after running:")
    print("python -c \"import psycopg2; print('psycopg2 available')\"")
    print("python -c \"import os; print(f'DATABASE_URL: {os.getenv(\"DATABASE_URL\", \"NOT SET\")}')\"")
    
    print("\n" + "=" * 50)
    print("1. BASIC CONNECTION TEST")
    print("=" * 50)
    print("""
python3 << 'EOF'
import os
import psycopg2
from urllib.parse import urlparse

# Parse DATABASE_URL
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("❌ DATABASE_URL not set")
    exit(1)

parsed = urlparse(db_url)
print(f"✅ Connecting to: {parsed.hostname}:{parsed.port}/{parsed.path[1:]}")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Test basic query
    cur.execute("SELECT 1")
    result = cur.fetchone()
    print(f"✅ Connection successful: {result[0]}")
    
    # Get PostgreSQL version
    cur.execute("SELECT version()")
    version = cur.fetchone()[0].split(',')[0]
    print(f"✅ PostgreSQL version: {version}")
    
    cur.close()
    conn.close()
    print("✅ Connection test passed!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
EOF
""")
    
    print("\n" + "=" * 50)
    print("2. LIST ALL TABLES")
    print("=" * 50)
    print("""
python3 << 'EOF'
import os
import psycopg2

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Get all tables in public schema
cur.execute(\"\"\"
    SELECT tablename, schemaname
    FROM pg_tables 
    WHERE schemaname = 'public'
    ORDER BY tablename;
\"\"\")

tables = cur.fetchall()
print(f"Found {len(tables)} tables:")
for table in tables:
    print(f"  - {table[0]}")

expected_tables = [
    'analytics_timeseries',
    'subscriptions', 
    'team_activities',
    'team_invites',
    'team_memberships',
    'teams',
    'thread_analytics',
    'threads',
    'usage_tracking',
    'user_sessions',
    'users'
]

print(f"\\nExpected: {len(expected_tables)} tables")
actual_tables = [t[0] for t in tables]
missing = [t for t in expected_tables if t not in actual_tables]
if missing:
    print(f"❌ Missing tables: {missing}")
else:
    print("✅ All expected tables found!")

cur.close()
conn.close()
EOF
""")
    
    print("\n" + "=" * 50)
    print("3. VERIFY CRITICAL TABLE STRUCTURES")
    print("=" * 50)
    print("""
python3 << 'EOF'
import os
import psycopg2

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

critical_tables = ['users', 'threads', 'subscriptions']

for table in critical_tables:
    print(f"\\n--- {table.upper()} TABLE ---")
    
    # Get column information
    cur.execute(\"\"\"
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = %s
        ORDER BY ordinal_position;
    \"\"\", (table,))
    
    columns = cur.fetchall()
    print(f"Columns ({len(columns)}):")
    for col in columns:
        nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
        default = f" DEFAULT {col[3]}" if col[3] else ""
        print(f"  - {col[0]}: {col[1]} {nullable}{default}")

cur.close()
conn.close()
EOF
""")
    
    print("\n" + "=" * 50)
    print("4. COUNT RECORDS IN ALL TABLES")
    print("=" * 50)
    print("""
python3 << 'EOF'
import os
import psycopg2

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Get all table names
cur.execute(\"\"\"
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'public'
    ORDER BY tablename;
\"\"\")

tables = [row[0] for row in cur.fetchall()]
total_records = 0

print("Record counts:")
for table in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  - {table}: {count} records")
        total_records += count
    except Exception as e:
        print(f"  - {table}: Error - {e}")

print(f"\\nTotal records: {total_records}")

cur.close()
conn.close()
EOF
""")
    
    print("\n" + "=" * 50)
    print("5. CHECK INDEXES")
    print("=" * 50)
    print("""
python3 << 'EOF'
import os
import psycopg2

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Get all indexes
cur.execute(\"\"\"
    SELECT schemaname, tablename, indexname, indexdef
    FROM pg_indexes 
    WHERE schemaname = 'public'
    ORDER BY tablename, indexname;
\"\"\")

indexes = cur.fetchall()
print(f"Found {len(indexes)} indexes:")

current_table = None
for idx in indexes:
    table_name = idx[1]
    if current_table != table_name:
        print(f"\\n{table_name}:")
        current_table = table_name
    
    index_name = idx[2]
    # Simplify index definition
    index_def = idx[3].replace(f'public.{table_name}', table_name)
    print(f"  - {index_name}")

cur.close()
conn.close()
EOF
""")
    
    print("\n" + "=" * 50)
    print("6. CHECK CONSTRAINTS")
    print("=" * 50)
    print("""
python3 << 'EOF'
import os
import psycopg2

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Get all constraints
cur.execute(\"\"\"
    SELECT tc.table_name, tc.constraint_name, tc.constraint_type,
           cc.check_clause
    FROM information_schema.table_constraints tc
    LEFT JOIN information_schema.check_constraints cc 
        ON tc.constraint_name = cc.constraint_name
    WHERE tc.table_schema = 'public'
    AND tc.constraint_type IN ('CHECK', 'UNIQUE', 'FOREIGN KEY')
    ORDER BY tc.table_name, tc.constraint_type;
\"\"\")

constraints = cur.fetchall()
print(f"Found {len(constraints)} constraints:")

current_table = None
for constraint in constraints:
    table_name = constraint[0]
    if current_table != table_name:
        print(f"\\n{table_name}:")
        current_table = table_name
    
    constraint_name = constraint[1]
    constraint_type = constraint[2]
    check_clause = constraint[3] if constraint[3] else ""
    
    print(f"  - {constraint_type}: {constraint_name}")
    if check_clause:
        print(f"    Check: {check_clause}")

cur.close()
conn.close()
EOF
""")
    
    print("\n" + "=" * 50)
    print("7. COMPREHENSIVE HEALTH CHECK")
    print("=" * 50)
    print("""
python3 << 'EOF'
import os
import psycopg2
from datetime import datetime

print(f"Database health check at {datetime.utcnow()}")
print("=" * 50)

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Database info
cur.execute("SELECT current_database(), current_user, version()")
db_info = cur.fetchone()
print(f"Database: {db_info[0]}")
print(f"User: {db_info[1]}")
print(f"Version: {db_info[2].split(',')[0]}")

# Database size
cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
db_size = cur.fetchone()[0]
print(f"Size: {db_size}")

# Table count
cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
table_count = cur.fetchone()[0]
print(f"Tables: {table_count}")

# Total records across all tables
cur.execute(\"\"\"
    SELECT SUM(n_tup_ins) as total_inserts,
           SUM(n_tup_upd) as total_updates,
           SUM(n_tup_del) as total_deletes,
           SUM(n_live_tup) as total_live_rows
    FROM pg_stat_user_tables
\"\"\")
stats = cur.fetchone()
if stats and stats[0]:
    print(f"Total live rows: {stats[3] or 0}")
    print(f"Total operations: {(stats[0] or 0) + (stats[1] or 0) + (stats[2] or 0)}")
else:
    print("No activity statistics available (new database)")

# Check for any errors
cur.execute("SELECT COUNT(*) FROM pg_stat_database_conflicts WHERE datname = current_database()")
conflicts = cur.fetchone()[0]
print(f"Database conflicts: {conflicts}")

print("\\n✅ Health check complete!")

cur.close()
conn.close()
EOF
""")
    
    print("\n" + "=" * 70)
    print("USAGE INSTRUCTIONS")
    print("=" * 70)
    print("""
1. SSH into your Render web service shell:
   render shell <your-service-name>

2. Navigate to the backend directory:
   cd backend/src

3. Run the verification script:
   python verify_database.py

4. Or run quick check:
   python verify_database.py --quick

5. For manual SQL verification, copy-paste the commands above
   into your Render shell one by one.

6. If you get import errors, install missing packages:
   pip install tabulate psycopg2-binary

The verification script will tell you:
- ✅ If all 11 tables were created successfully
- ✅ If all indexes and constraints are in place  
- ✅ Current record counts in each table
- ❌ Any errors or missing components

Expected result: All 11 tables with 0 records each (fresh database)
""")

if __name__ == "__main__":
    print_manual_commands()