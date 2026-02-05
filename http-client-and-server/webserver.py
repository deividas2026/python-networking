import socket
import sys

port = 28333

if len(sys.argv) == 2:
    try:
        port = int(sys.argv[1])
    except ValueError:
        sys.exit("Port must be an integer") 
elif len(sys.argv) != 1:
    sys.exit("Usage: webserver.py [port]")

payload = b"Hello from server"
response = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/plain\r\n"
    f"Content-Length: {len(payload)}\n"
    "Connection: close\r\n"
    "\r\n"
).encode("ISO-8859-1")
response += payload

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", port))
server.listen()

while True:
    new_conn, new_addr = server.accept()
    request = b"" 

    while True:
        buffer = new_conn.recv(4096)
        request += buffer
        if b"\r\n\r\n" in request or len(buffer) == 0:
            break
        
    new_conn.sendall(response)
    new_conn.close()
