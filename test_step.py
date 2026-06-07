"""分步集成测试 - admin登录 → 申请 → 审核 → 登录 → 看板"""
import requests, json, sys, random

BASE = 'http://127.0.0.1:10011/api/v1'
TIMEOUT = 10


def step(name, fn):
    print(f'\n>>> {name}')
    sys.stdout.flush()
    try:
        result = fn()
        if isinstance(result, requests.Response):
            print(f'Status: {result.status_code}')
            try:
                data = result.json()
                txt = json.dumps(data, ensure_ascii=False, indent=2)[:1500]
            except Exception:
                txt = result.text[:500]
            print(txt)
            sys.stdout.flush()
        return result
    except Exception as e:
        print(f'ERROR: {type(e).__name__}: {e}')
        sys.stdout.flush()
        raise


# 1. 管理员登录
r = step('Admin Login (guoxudong/1)', lambda: requests.post(
    f'{BASE}/auth/login',
    json={'username': 'guoxudong', 'password': '1'},
    timeout=TIMEOUT))
assert r.status_code == 200, f'Login failed: {r.status_code}'
admin_token = r.json()['data']['access_token']
admin_h = {'Authorization': f'Bearer {admin_token}'}

# 2. 灌入演示数据
r = step('Seed Demo Data', lambda: requests.post(
    f'{BASE}/demo/seed', headers=admin_h, timeout=TIMEOUT))
print('Seed created:', r.json()['data']['created'])
sys.stdout.flush()

# 3. 列出组织结构
r = step('List Org Companies', lambda: requests.get(
    f'{BASE}/org/companies', headers=admin_h, timeout=TIMEOUT))
companies = r.json().get('data') or []
print(f'\n[INFO] 共 {len(companies)} 个公司')
for c in companies:
    print(f"  · {c.get('name')} ({c.get('code')})")
    for d in c.get('departments', []):
        print(f"      · {d.get('name')} ({d.get('code')})")
        for t in d.get('teams', []):
            print(f"          - {t.get('name')} ({t.get('code')}) members={t.get('member_count', 0)}")
sys.stdout.flush()

# 4. 提交新申请
test_username = f'tester{random.randint(1000, 9999)}'
r = step(f'Submit Application ({test_username})', lambda: requests.post(
    f'{BASE}/auth/apply',
    json={
        'username': test_username,
        'password': 'tester123',
        'nickname': f'虚拟用户 {test_username}',
        'email': f'{test_username}@example.com',
        'phone': '13800000000',
        'reason': '测试注册流程：查看个人和团队看板'
    },
    timeout=TIMEOUT))
print('Apply result:', r.json())
sys.stdout.flush()

# 5. 管理员查看申请列表
r = step('List Applications', lambda: requests.get(
    f'{BASE}/auth/applications', headers=admin_h, timeout=TIMEOUT))
apps = r.json()['data']['list']
pending = [a for a in apps if a['status'] == 'pending']
print(f'Apps total={len(apps)}, pending={len(pending)}')
sys.stdout.flush()

# 6. 找 FE 团队 ID
fe_team_id = None
for comp in companies:
    for d in comp.get('departments', []):
        for t in d.get('teams', []):
            if t.get('code') == 'FE':
                fe_team_id = t.get('id')
print(f'FE team id = {fe_team_id}')
sys.stdout.flush()

# 7. 审核通过所有 pending
for app in pending:
    r = step(f"Approve #{app['id']} {app['username']}", lambda a=app: requests.post(
        f'{BASE}/auth/applications/{a["id"]}/approve',
        headers=admin_h,
        json={
            'role': 'editor',
            'team_id': str(fe_team_id) if fe_team_id else '',
            'comment': 'OK，欢迎加入',
        },
        timeout=TIMEOUT))
    print('Approve result:', r.json())
    sys.stdout.flush()

# 8. 维护人员权限：把 bob 从 FE 移到 BE
r = step('Admin: List users', lambda: requests.get(
    f'{BASE}/user-admin/list', headers=admin_h, timeout=TIMEOUT))
users_data = r.json().get('data') or []
print(f'共 {len(users_data)} 个用户')
bob_user = next((u for u in users_data if u['username'] == 'bob'), None)
be_team_id = None
for comp in companies:
    for d in comp.get('departments', []):
        for t in d.get('teams', []):
            if t.get('code') == 'BE':
                be_team_id = t.get('id')

if bob_user and be_team_id:
    r = step('Admin: Add bob to BE team', lambda: requests.post(
        f'{BASE}/user-admin/{bob_user["id"]}/teams',
        headers=admin_h,
        json={'team_id': be_team_id, 'role': 'member'},
        timeout=TIMEOUT))
    print('Add result:', r.json())
    sys.stdout.flush()

# 9. 上传组织结构（测试）
import io
upload_data = {
    "companies": [
        {
            "name": "新分公司",
            "code": "NEW",
            "departments": [
                {"name": "新产品部", "code": "NPD", "teams": [
                    {"name": "创新组", "code": "INNO", "description": "创新业务"},
                ]},
            ]
        }
    ]
}
r = step('Upload Org Structure', lambda: requests.post(
    f'{BASE}/org/upload',
    headers=admin_h,
    files={'file': ('org.json', json.dumps(upload_data), 'application/json')},
    timeout=TIMEOUT))
print('Upload result:', r.json())
sys.stdout.flush()

# 10. 验证组织结构已新增
r = step('Verify new org', lambda: requests.get(
    f'{BASE}/org/companies', headers=admin_h, timeout=TIMEOUT))
companies = r.json().get('data') or []
new_co = next((c for c in companies if c.get('code') == 'NEW'), None)
print(f'新分公司已存在: {bool(new_co)}')
if new_co:
    print(f"  - {new_co['name']}: {len(new_co.get('departments', []))} 部门")
sys.stdout.flush()

# 11. tester 登录
r = step(f'{test_username} Login', lambda: requests.post(
    f'{BASE}/auth/login',
    json={'username': test_username, 'password': 'tester123'},
    timeout=TIMEOUT))
if r.status_code == 200:
    t_tok = r.json()['data']['access_token']
    t_h = {'Authorization': f'Bearer {t_tok}'}
    r = step('Tester: Personal Kanban', lambda: requests.get(
        f'{BASE}/demo/kanban/personal', headers=t_h, timeout=TIMEOUT))
    r = step('Tester: My Teams', lambda: requests.get(
        f'{BASE}/demo/kanban/teams', headers=t_h, timeout=TIMEOUT))
    teams = r.json()['data']['teams']
    print(f'所属团队数: {len(teams)}')
    if teams:
        r = step(f"Tester: Team Kanban #{teams[0]['team_id']}", lambda tid=teams[0]['team_id']: requests.get(
            f'{BASE}/demo/kanban/team/{tid}', headers=t_h, timeout=TIMEOUT))
else:
    print(f'登录失败: {r.status_code} {r.text[:200]}')

# 12. Alice 登录（虚拟用户）
r = step('Alice Login', lambda: requests.post(
    f'{BASE}/auth/login',
    json={'username': 'alice', 'password': 'alice123'},
    timeout=TIMEOUT))
if r.status_code == 200:
    a_tok = r.json()['data']['access_token']
    a_h = {'Authorization': f'Bearer {a_tok}'}
    r = step('Alice: Personal Kanban', lambda: requests.get(
        f'{BASE}/demo/kanban/personal', headers=a_h, timeout=TIMEOUT))
    r = step('Alice: My Teams', lambda: requests.get(
        f'{BASE}/demo/kanban/teams', headers=a_h, timeout=TIMEOUT))
    teams = r.json()['data']['teams']
    print(f'Alice 所属团队: {[t["team_name"] for t in teams]}')
    if teams:
        r = step(f"Alice: Team Kanban #{teams[0]['team_id']}", lambda tid=teams[0]['team_id']: requests.get(
            f'{BASE}/demo/kanban/team/{tid}', headers=a_h, timeout=TIMEOUT))

print('\n=== ALL DONE ===')
