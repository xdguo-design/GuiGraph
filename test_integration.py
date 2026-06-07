"""集成测试 - 输出到文件"""
import requests, json, sys

BASE = 'http://localhost:10011/api/v1'
log = []

def show(title, r):
    try:
        data = r.json()
        text = json.dumps(data, ensure_ascii=False, indent=2)[:1500]
    except Exception:
        text = r.text[:500]
    log.append(f'\n=== {title} ===\nStatus: {r.status_code}\n{text}\n')
    return r

# 1. 管理员登录
r = show('Admin Login (guoxudong/1)',
    requests.post(f'{BASE}/auth/login', json={'username': 'guoxudong', 'password': '1'}))

admin_token = r.json()['data']['access_token']
admin_h = {'Authorization': f'Bearer {admin_token}'}

# 2. 提交注册申请
r = show('Submit Application (tester)',
    requests.post(f'{BASE}/auth/apply', json={
        'username': 'tester',
        'password': 'tester123',
        'nickname': '虚拟用户 tester',
        'email': 'tester@example.com',
        'phone': '13800000000',
        'reason': '测试注册流程：查看个人和团队看板'
    }))

# 3. 管理员查看申请
r = show('Admin: List Applications',
    requests.get(f'{BASE}/auth/applications', headers=admin_h))
apps = r.json().get('data', {}).get('list', [])
pending = [a for a in apps if a['status'] == 'pending']
log.append(f'[INFO] pending = {len(pending)}\n')

# 4. 列出组织 - 找 FE 团队
r = show('List Org Companies',
    requests.get(f'{BASE}/org/companies', headers=admin_h))
companies = r.json().get('data', [])

fe_team_id = None
dept_id_for_fe = None
company_id = None
for comp in companies:
    company_id = comp.get('id') or comp.get('company_id')
    for d in comp.get('departments', []):
        for t in d.get('teams', []):
            if t.get('code') == 'FE':
                fe_team_id = t.get('id')
                dept_id_for_fe = d.get('id')
log.append(f'[INFO] FE team_id={fe_team_id} dept={dept_id_for_fe} comp={company_id}\n')

# 5. 审核通过
for app in pending:
    r = show(f"Approve #{app['id']} {app['username']}",
        requests.post(f'{BASE}/auth/applications/{app["id"]}/approve',
            headers=admin_h, json={
                'role': 'editor',
                'team_id': str(fe_team_id) if fe_team_id else '',
                'comment': '测试通过，加入 FE 团队'
            }))

# 6. 灌入演示数据
r = show('Seed Demo Data', requests.post(f'{BASE}/demo/seed', headers=admin_h))

# 7. tester 登录并查看板
r = show('Tester Login', requests.post(f'{BASE}/auth/login',
    json={'username': 'tester', 'password': 'tester123'}))

if r.status_code == 200:
    t_tok = r.json()['data']['access_token']
    t_h = {'Authorization': f'Bearer {t_tok}'}
    show('Tester: Personal Kanban', requests.get(f'{BASE}/demo/kanban/personal', headers=t_h))
    r = show('Tester: My Teams', requests.get(f'{BASE}/demo/kanban/teams', headers=t_h))
    teams = r.json().get('data', {}).get('teams', [])
    if teams:
        show(f"Tester: Team Kanban #{teams[0]['team_id']}",
             requests.get(f'{BASE}/demo/kanban/team/{teams[0]["team_id"]}', headers=t_h))

# 8. Alice 登录（FE 团队已存在虚拟用户）
r = show('Alice Login', requests.post(f'{BASE}/auth/login',
    json={'username': 'alice', 'password': 'alice123'}))

if r.status_code == 200:
    a_tok = r.json()['data']['access_token']
    a_h = {'Authorization': f'Bearer {a_tok}'}
    show('Alice: Personal Kanban', requests.get(f'{BASE}/demo/kanban/personal', headers=a_h))
    r = show('Alice: My Teams', requests.get(f'{BASE}/demo/kanban/teams', headers=a_h))
    teams = r.json().get('data', {}).get('teams', [])
    if teams:
        show(f"Alice: Team Kanban #{teams[0]['team_id']}",
             requests.get(f'{BASE}/demo/kanban/team/{teams[0]["team_id"]}', headers=a_h))

with open('test-output.log', 'w', encoding='utf-8') as f:
    f.write(''.join(log))
print('Output written to test-output.log, total lines:', len(log))
