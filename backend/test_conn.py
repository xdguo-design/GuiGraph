import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
try:
    s.connect(('127.0.0.1', 10011))
    print('Connected!')
    s.send(b'GET /health HTTP/1.0\r\nHost: localhost\r\n\r\n')
    data = s.recv(4096)
    print('Response:', data.decode('utf-8', errors='replace'))
except Exception as e:
    print(f'Error: {e}')
finally:
    s.close()
