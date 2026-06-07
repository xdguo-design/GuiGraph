import requests, json

# 1. Login
login_resp = requests.post('http://127.0.0.1:8000/api/v1/auth/login', json={'username': 'guoxudong', 'password': '1234'})
print('=== LOGIN ===')
print('Status:', login_resp.status_code)
login_data = login_resp.json()
print(json.dumps(login_data, indent=2, ensure_ascii=False))

token = login_data.get('data', {}).get('access_token', '')
if not token:
    print('ERROR: No token received')
    exit(1)

# 2. Call Gantt API
headers = {'Authorization': 'Bearer ' + token}
gantt_resp = requests.get('http://127.0.0.1:8000/api/v1/dashboard/gantt?start_date=2026-06-01&end_date=2026-06-30', headers=headers)
print('\n=== GANTT API ===')
print('Status:', gantt_resp.status_code)
gantt_data = gantt_resp.json()
print(json.dumps(gantt_data, indent=2, ensure_ascii=False))

# Validate
data = gantt_data.get('data', {})
tasks = data.get('tasks', [])
deps = data.get('dependencies', [])
print('\n=== VALIDATION ===')
print('code:', gantt_data.get('code'))
print('tasks count:', len(tasks))
print('dependencies count:', len(deps))
if tasks:
    t = tasks[0]
    print('First task fields:', list(t.keys()))
    print('First task:', json.dumps(t, ensure_ascii=False))
