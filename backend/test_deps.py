import requests, json

# Login
login_resp = requests.post('http://127.0.0.1:8000/api/v1/auth/login', json={'username': 'guoxudong', 'password': '1234'})
login_data = login_resp.json()
token = login_data.get('data', {}).get('access_token', '')
headers = {'Authorization': 'Bearer ' + token}

# TC013: Check database dependency table structure
# Check if biz_change_dependency table exists by querying the Gantt API
gantt_resp = requests.get('http://127.0.0.1:8000/api/v1/dashboard/gantt?start_date=2026-06-01&end_date=2026-06-30', headers=headers)
gantt_data = gantt_resp.json()
deps = gantt_data.get('data', {}).get('dependencies', [])
tasks = gantt_data.get('data', {}).get('tasks', [])
print('=== TC013: Database dependency table ===')
print('Dependencies count:', len(deps))
print('Tasks count:', len(tasks))
if tasks:
    task_ids = [t['id'] for t in tasks]
    print('Task IDs:', task_ids)

# Now insert test dependency data via SQLite
import sqlite3
db_path = 'D:/GuiGraph/backend/guigraph.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check table structure
cursor.execute("PRAGMA table_info(biz_change_dependency)")
columns = cursor.fetchall()
print('\nTable structure:')
for col in columns:
    print(f'  {col}')

# Check foreign keys
cursor.execute("PRAGMA foreign_key_list(biz_change_dependency)")
fks = cursor.fetchall()
print('\nForeign keys:')
for fk in fks:
    print(f'  {fk}')

# Check existing data
cursor.execute("SELECT * FROM biz_change_dependency")
existing = cursor.fetchall()
print('\nExisting dependency records:', len(existing))

# Insert test dependencies if not exist
if len(existing) == 0 and len(tasks) >= 3:
    # Use the first 3 task IDs
    ids = [int(tasks[i]['id']) for i in range(min(3, len(tasks)))]
    cursor.execute(
        "INSERT INTO biz_change_dependency (from_change_id, to_change_id, dependency_type, created_by) VALUES (?, ?, 'FS', 1)",
        (ids[0], ids[1])
    )
    cursor.execute(
        "INSERT INTO biz_change_dependency (from_change_id, to_change_id, dependency_type, created_by) VALUES (?, ?, 'FS', 1)",
        (ids[1], ids[2])
    )
    conn.commit()
    print(f'\nInserted 2 test dependencies: {ids[0]}->{ids[1]}->{ids[2]}')
else:
    print('\nNo dependencies inserted (existing:', len(existing), ', tasks:', len(tasks), ')')

conn.close()

# TC005: Verify dependencies appear in Gantt API
gantt_resp2 = requests.get('http://127.0.0.1:8000/api/v1/dashboard/gantt?start_date=2026-06-01&end_date=2026-06-30', headers=headers)
gantt_data2 = gantt_resp2.json()
deps2 = gantt_data2.get('data', {}).get('dependencies', [])
print('\n=== TC005: Dependency lines ===')
print('Dependencies after insert:', len(deps2))
for d in deps2:
    print(f'  {d}')
