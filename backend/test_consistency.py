import requests, json

# Login
login_resp = requests.post('http://127.0.0.1:8000/api/v1/auth/login', json={'username': 'guoxudong', 'password': '1234'})
login_data = login_resp.json()
token = login_data.get('data', {}).get('access_token', '')
headers = {'Authorization': 'Bearer ' + token}

# Query the same date range as the UI (5/18 to 7/14 of 2026)
gantt_resp = requests.get('http://127.0.0.1:8000/api/v1/dashboard/gantt?start_date=2026-05-18&end_date=2026-07-14', headers=headers)
gantt_data = gantt_resp.json()
api_tasks = gantt_data.get('data', {}).get('tasks', [])
api_deps = gantt_data.get('data', {}).get('dependencies', [])

print('=== TC014: API vs UI consistency ===')
print(f'API task count: {len(api_tasks)}')
print(f'API dependency count: {len(api_deps)}')
print('API tasks:')
for t in api_tasks:
    print(f'  {t["id"]}: {t["content"]} ({t["start_date"]})')
print('API dependencies:')
for d in api_deps:
    print(f'  {d}')
