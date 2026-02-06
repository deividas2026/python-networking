import socket
import sys
from response import send_response

port = 28333

if len(sys.argv) == 2:
    try:
        port = int(sys.argv[1])
    except ValueError:
        sys.exit("Port must be an integer") 
elif len(sys.argv) != 1:
    sys.exit("Usage: webserver.py [port]")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", port))
server.listen()
server_ip, server_port = server.getsockname()
print(f"Server is listening on: {server_ip}:{server_port}")

while True:
    new_conn, new_addr = server.accept()
    new_conn.settimeout(5)
    print(f"New connection: {new_addr[0]}:{new_addr[1]}")

    invalid_headers_error = False
    timeout_error = False
    connection_closed_error = False
    request = b"" 

    while True:
        try:
            buffer = new_conn.recv(4096)
        except TimeoutError:
            timeout_error = True
            break

        request += buffer
        if b"\r\n\r\n" in request:
            break
        if len(buffer) == 0:
            connection_closed_error = True 
            break
    
    if connection_closed_error:
        send_response(new_conn, 400, "Connection closed by client")
        continue
    
    if timeout_error:
        send_response(new_conn, 408, "Client took to long to respond")
        continue

    request_header, request_body = request.split(b"\r\n\r\n")
    header_fields = request_header.decode("ISO-8859-1").split("\r\n")
    first_header_field = header_fields[0].strip().split(" ")

    if len(first_header_field) != 3:
        send_response(new_conn, 400, "Invalid request header syntax")
        continue

    method, path, protocol = first_header_field 
    print(f"Request method: {method.upper()}")
    headers = {} 

    for header_field in header_fields[1:]:
        header_name_value = header_field.strip().split(":", 1)      
        if len(header_name_value) != 2:
            invalid_headers_error = True
            break
        name, value = header_name_value
        headers.update({name.strip().lower(): value.strip()})
    
    if invalid_headers_error:
        send_response(new_conn, 400, "Invalid request header syntax")
        continue
    
    if method.upper() not in ["POST", "PUT", "PATCH"]:
        send_response(new_conn, 200)
        continue

    content_length = headers.get("content-length")
    if content_length is None:
        send_response(new_conn, 411, "Missing Content-Length header")
        continue
    
    try:
        content_length = int(content_length)
    except ValueError:
        send_response(new_conn, 400, "Invalid request header syntax")
        continue
        
    remaining = content_length - len(request_body)
    while remaining > 0:
        try:
            buffer = new_conn.recv(min(4096, remaining))
        except TimeoutError:
            timeout_error = True
            break

        request_body += buffer 
        remaining -= len(buffer)
        if len(buffer) == 0:
            connection_closed_error = True
            break
    
    if connection_closed_error:
        send_response(new_conn, 400, "Connection closed by client")
        continue
    
    if timeout_error:
        send_response(new_conn, 408, "Client took to long to respond")
        continue
            
    send_response(new_conn, 200)
    request_body = request_body.decode("ISO-8859-1")
    print(f"Request body: {request_body}")
