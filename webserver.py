import time
import socket, sys
from get_time import get_time

port = 20123

if len(sys.argv) == 2:
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Invalid port number, server will use the default one")


http_response = (
    f"HTTP/1.1 200 OK\r\n"
    f"Content-Type: text/plain\r\n"
    f"Content-Length: 6\r\n"
    f"Connection: close\r\n"
    f"\r\n"
    f"Hello!"
)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", port))
s.listen()
a, p = s.getsockname()
print(f"{get_time()}: Server is listening on {a}:{p}")

while True:
    conn, addr = s.accept()
    print(f"{get_time()}: New connection {addr[0]}:{addr[1]}")   
    request = b""
 
    while True:
        d = conn.recv(1024)
        if not d:
            break
        request += d
        if b"\r\n\r\n" in request:
            break

    conn.sendall(http_response.encode("ISO-8859-1"))
    conn.close()
