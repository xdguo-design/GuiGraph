"""调试脚本: 检查 API 实际响应."""
import json
import urllib.error
import urllib.request


def get(url, token=None, accept_json=True):
    h = {}
    if accept_json:
        h["Accept"] = "application/json"
    if token:
        h["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def post(url, body, token=None, accept_json=True):
    h = {"Content-Type": "application/json"}
    if accept_json:
        h["Accept"] = "application/json"
    if token:
        h["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def put(url, body, token=None):
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h, method="PUT")
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def patch_(url, body, token):
    h = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h, method="PATCH")
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def del_(url, token):
    h = {"Accept": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, headers=h, method="DELETE")
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


# 1. login
code, body = post("http://127.0.0.1:8000/api/v1/auth/login",
                  {"username": "guoxudong", "password": "1234"})
print("[login]", code, body[:200])
token = json.loads(body)["data"]["access_token"]
refresh = json.loads(body)["data"]["refresh_token"]

# 2. AUTH-04: refresh token
print("\n[AUTH-04] refresh_token as query:")
r = urllib.request.Request(
    f"http://127.0.0.1:8000/api/v1/auth/refresh?refresh_token={refresh}",
    headers={"Accept": "application/json"}, method="POST",
)
try:
    with urllib.request.urlopen(r, timeout=5) as resp:
        print(" OK:", resp.status, resp.read().decode()[:200])
except urllib.error.HTTPError as e:
    print(" ERR:", e.code, e.read().decode()[:200])

# 3. CHG-05: create change
print("\n[CHG-05] create change")
code, body = post(
    "http://127.0.0.1:8000/api/v1/changes",
    {"version_id": 1, "change_type": "db", "content": "x", "change_reason": "requirement"},
    token=token,
)
print(" ", code, body[:400])

# 4. CHG-08: detail nonexistent
print("\n[CHG-08] detail 9999999")
code, body = get("http://127.0.0.1:8000/api/v1/changes/9999999", token=token)
print(" ", code, body[:200])

# 5. CHG-09: update
print("\n[CHG-09] update first change")
code, body = put("http://127.0.0.1:8000/api/v1/changes/1", {"content": "updated"}, token=token)
print(" ", code, body[:200])

# 6. CHG-10: approve
print("\n[CHG-10] approve")
code, body = post("http://127.0.0.1:8000/api/v1/changes/1/approve", {"comment": "ok"}, token=token)
print(" ", code, body[:200])

# 7. KAN-04: heatmap
print("\n[KAN-04] heatmap 2025-07")
code, body = get("http://127.0.0.1:8000/api/v1/dashboard/kanban?month=2025-07", token=token)
print(" ", code, body[:500])

# 8. KAN-03 invalid month
print("\n[KAN-03] invalid month")
code, body = get("http://127.0.0.1:8000/api/v1/dashboard/kanban?month=invalid", token=token)
print(" ", code, body[:200])

# 9. GIT-02 create repo
print("\n[GIT-02] create repo")
code, body = post(
    "http://127.0.0.1:8000/api/v1/git/repos",
    {"name": f"auto-repo-{int(__import__('time').time())}",
     "url": "https://github.com/auto/test.git", "platform": "github"},
    token=token,
)
print(" ", code, body[:400])

# 10. JNK-04 update
print("\n[JNK-04] update jenkins 1")
code, body = put("http://127.0.0.1:8000/api/v1/jenkins/instances/1", {"name": "r"}, token=token)
print(" ", code, body[:300])

# 11. UPG-01 list
print("\n[UPG-01] upgrades list")
code, body = get("http://127.0.0.1:8000/api/v1/upgrades?page=1&page_size=10", token=token)
print(" ", code, body[:400])

# 12. UPG-02 version filter
print("\n[UPG-02] upgrades version filter")
code, body = get("http://127.0.0.1:8000/api/v1/upgrades?version=v1.0.0", token=token)
print(" ", code, body[:200])

# 13. UPG-06 detail 9999
print("\n[UPG-06] upgrades detail 99999")
code, body = get("http://127.0.0.1:8000/api/v1/upgrades/99999", token=token)
print(" ", code, body[:200])

# 14. AI-02 rag analyze
print("\n[AI-02] rag analyze")
code, body = post("http://127.0.0.1:8000/api/v1/ai/rag/analyze", {"content": "x"}, token=token)
print(" ", code, body[:200])

# 15. AI-04 empty query
print("\n[AI-04] empty query")
code, body = post("http://127.0.0.1:8000/api/v1/ai/rag/search", {"query": "", "top_k": 3}, token=token)
print(" ", code, body[:200])

# 16. PRM-01
print("\n[PRM-01] /permissions/matrix")
code, body = get("http://127.0.0.1:8000/api/v1/permissions/matrix", token=token)
print(" ", code, body[:200])

# 17. AUD-01
print("\n[AUD-01] /audit")
code, body = get("http://127.0.0.1:8000/api/v1/audit?page=1&page_size=10", token=token)
print(" ", code, body[:500])

# 18. ADM-01 list users
print("\n[ADM-01] /user-admin/list")
code, body = get("http://127.0.0.1:8000/api/v1/user-admin/list", token=token)
print(" ", code, body[:500])

# 19. ATT-01 upload
print("\n[ATT-01] upload")
boundary = "----FormBoundary123"
png_bytes = b"abc123"
parts = [
    f"--{boundary}\r\n".encode(),
    b'Content-Disposition: form-data; name="file"; filename="auto.txt"\r\n',
    b"Content-Type: application/octet-stream\r\n\r\n",
    b"hello world",
    f"\r\n--{boundary}--\r\n".encode(),
]
body_bytes = b"".join(parts)
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/attachment/upload",
    data=body_bytes,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print(" ", resp.status, resp.read().decode()[:300])
except urllib.error.HTTPError as e:
    print(" ", e.code, e.read().decode()[:300])

# 20. Frontend page Accept */*
print("\n[FRONTEND] /login accept=*/*")
r = urllib.request.Request("http://localhost:10010/login", headers={"Accept": "*/*"})
try:
    with urllib.request.urlopen(r, timeout=5) as resp:
        print(" ", resp.status, len(resp.read()))
except urllib.error.HTTPError as e:
    print(" ", e.code, e.read().decode()[:200])
