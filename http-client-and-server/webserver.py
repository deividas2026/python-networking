import re
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
server_ip, server_port = server.getsockname()
print(f"Server is listening on: {server_ip}:{server_port}")

while True:
    new_conn, new_addr = server.accept()
    new_conn_closed = False
    print(f"New connection: {new_addr[0]}:{new_addr[1]}")
    request = b"" 

    while True:
        buffer = new_conn.recv(4096)
        request += buffer
        if b"\r\n\r\n" in request:
            break
        if len(buffer) == 0:
            new_conn_closed = True 
            break
    
    if new_conn_closed:
        new_conn.close()
        continue

    request_header, request_body = request.split(b"\r\n\r\n")
    header_fields = request_header.decode("ISO-8859-1").split("\r\n")

    request_method = header_fields[0].split(" ")[0]
    content_type = None
    content_length = None

    for header_field in header_fields:
        header_field = header_field.strip().lower()
        if header_field.startswith("content-type:"):
            content_type = header_field.split(":")[1].strip()
        elif header_field.startswith("content-length"):
            content_length = header_field.split(":")[1].strip()
        if content_length and content_type:
            break
     
    if content_type is None or content_length is None:
        new_conn.sendall(response)
        new_conn.close()
        continue
    
    try:
        content_length = int(content_length)
    except ValueError:
        new_conn.sendall(response)
        new_conn.close()
        continue

    while len(request_body) < content_length:
        buffer = new_conn.recv(4096)
        request_body += buffer
        if len(buffer) == 0:
            break
    
    if len(request_body) != content_length:
        new_conn.sendall(response)
        new_conn.close()
        continue

    request_body = request_body.decode("ISO-8859-1")
    print(f"Request method: {request_method}")
    print(f"Payload: {request_body}")
    new_conn.sendall(response)
    new_conn.close()
