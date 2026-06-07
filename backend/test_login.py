import socket
import json

# Test login endpoint
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
try:
    s.connect(('127.0.0.1', 10011))
    body = json.dumps({"username": "guoxudong", "password": "1"})
    request = f"POST /api/v1/auth/login HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n{body}"
    s.send(request.encode())
    data = b""
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        data += chunk
    print('Response:', data.decode('utf-8', errors='replace'))
except Exception as e:
    print(f'Error: {e}')
finally:
    s.close()
