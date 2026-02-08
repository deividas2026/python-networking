import json
import os
import socket
import sys

FILES_DIR = os.path.abspath("files")
port = 28333
supported_mime_types = {
    ".txt": "text/plain",
    ".html": "text/html",
    ".css": "text/css",
}

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

while True:
    new_conn, new_addr = server.accept()
    request = b"" 
    error = False

    while True:
        buffer = new_conn.recv(4096)
        if len(buffer) == 0:
            error = True
            break

        request += buffer
        if b"\r\n\r\n" in request:
            break
    
    if error:
        new_conn.close()
        continue
        
    request_header, request_body = request.split(b"\r\n\r\n")
    header_fields = request_header.decode("ISO-8859-1").split("\r\n")
    first_header_field = header_fields[0].strip().split(" ")
    method, path, protocol = first_header_field 
    #print(json.dumps(header_fields, indent=4))
    
    relative_path = path.lstrip("/")
    joined_path = os.path.join(FILES_DIR, relative_path)
    final_path = os.path.abspath(joined_path)

    if final_path == FILES_DIR:
        mime_type = "text/html"
        files = os.listdir(FILES_DIR)
        html_links = []
        for file in files:
            html_links.append(f'<a href="{file}">{file}</a>')
        
        html_links = "".join(html_links)
        response_body = (
            "<!DOCTYPE html>"
            "<html>"
                "<head>"
                    '<link rel="stylesheet" href="style.css">'
                "</head>"
                "<body>"
                    f"{html_links}" 
                "</body>"
            "</html>"
        ).encode("ISO-8859-1")
        response_header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "\r\n"
        ).encode("ISO-8859-1")
        response = response_header + response_body
        new_conn.sendall(response) 
        new_conn.close()
    elif final_path.startswith(FILES_DIR + os.sep):
        file_extension = os.path.splitext(final_path)[-1]
        mime_type = supported_mime_types.get(file_extension)

        try:
            with open(final_path, "rb") as fp:
                data = fp.read()
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    f"Content-Type: {mime_type}\r\n"
                    f"Content-Length: {len(data)}\r\n"
                    "\r\n"
                ).encode("ISO-8859-1")
                response += data
                new_conn.sendall(response)
                new_conn.close()
        except:
            data = b"Not Found"
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(data)}\r\n"
                "\r\n"
            ).encode("ISO-8859-1")
            response += data
            new_conn.sendall(response)
            new_conn.close()
    else:
        data = b"Not Found"
        response = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(data)}\r\n"
            "\r\n"
        ).encode("ISO-8859-1")
        response += data
        new_conn.sendall(response)
        new_conn.close()
