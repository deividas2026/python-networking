import socket
import sys

port = 80

if len(sys.argv) == 3:
    try:
        port = int(sys.argv[2])
    except ValueError:
        sys.exit("Port must be an integer") 
    if port > 65535 or port < 0:
        sys.exit("Port must be between 0 and 65535")
elif len(sys.argv) != 2:
    sys.exit("Usage: webclient.py hostname [port]")
    
host = sys.argv[1]
host_header = host if port in [80, 443] else f"{host}:{port}"

request = (
    "GET / HTTP/1.1\r\n"
    f"Host: {host_header}\r\n"
    "User-Agent: webclient/0.1\r\n"
    "Accept: */*\r\n"
    "Connection: close\r\n"
    "\r\n"
).encode("ISO-8859-1")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
client_socket.sendall(request)
response = b""

while True:
    data = client_socket.recv(4096)
    response += data
    if len(data) == 0:
        break

client_socket.close()
response = response.decode("ISO-8859-1")
print(response)
