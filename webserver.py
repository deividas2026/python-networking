import time
import socket
import sys
import os
from get_time import printt
from _404 import send_404

SERVER_ROOT = os.path.abspath(".")
PORT = 20123
HOST = "127.0.0.1"

mime_types = {
    ".gif": "image/gif",
    ".txt": "text/plain",
    ".html": "text/html",
    ".css": "text/css",
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
server_ip, server_port = server.getsockname()
printt(f"Server is listening on {server_ip}:{server_port}")

while True:
    new_connection, new_connection_socket_name = server.accept()
    new_connection_ip, new_connection_port = new_connection_socket_name
    printt(f"New connection {new_connection_ip}:{new_connection_port}")   
    
    buffer = b""
    while True:
        bytes_received = new_connection.recv(4096)
        if not bytes_received:
            new_connection.close()
            break

        buffer += bytes_received
        if b"\r\n\r\n" in buffer:
            break
    
    header = buffer.split(b"\r\n\r\n")[0]
    first_line_of_header = header.split(b"\r\n")[0].decode("ISO-8859-1")
    method, requested_path, _ = first_line_of_header.split(" ")
    file_path = os.path.sep.join((SERVER_ROOT, requested_path))
    file_path = os.path.abspath(file_path)

    if not file_path.startswith(SERVER_ROOT):
        new_connection.sendall(send_404())
        new_connection.close()

    else:
        if file_path == SERVER_ROOT:
            files = os.listdir(file_path)
            links = []
            for file in files:
                f_name, f_extension = os.path.splitext(file)
                if f_extension in mime_types:
                    links.append(f'<a href="{file}">{file}</a>')
                    
            response_body = []
            response_body.extend([
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "<link rel=\"stylesheet\" href=\"style.css\">",
                "</head>",
                "<body>",
                "<h1>Available files</h1>",
            ])
            response_body.extend(links)
            response_body.extend([
                "</body>",
                "</html>",
            ])

            response_body = "".join(response_body).encode("ISO-8859-1")

            response_header = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode("ISO-8859-1") 

            new_connection.sendall(response_header + response_body)
            new_connection.close()
            continue
                 
        try:
            with open(file_path, "rb") as f:
                fb = f.read()
                _, extension = os.path.splitext(file_path)
                response = (
                    "HTTP/1.1 200 OK\r\n"    
                    f"Content-Type: {mime_types[extension]}\r\n"
                    f"Content-Length: {len(fb)}\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("ISO-8859-1")

                new_connection.sendall(response + fb)
                new_connection.close()
        except:
            new_connection.sendall(send_404())
            new_connection.close()
