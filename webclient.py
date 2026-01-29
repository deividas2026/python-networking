import socket, sys, os

port = 80

if len(sys.argv) == 2:
    hostname = sys.argv[1]
elif len(sys.argv) == 3:
    hostname = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        sys.exit("Invalid port number")
else:
    sys.exit(f"Usage: {sys.argv[0]} hostname [port]")

http_request = (
    f"GET / HTTP/1.1\r\n"
    f"Host: {hostname}\r\n"
    # f"Accept: text/html\r\n"
    # f"User-Agent: my-awesome-client\r\n"
    f"Connection: close\r\n"
    f"\r\n"
)

s = socket.socket()
s.connect((hostname, port))
s.sendall(http_request.encode("ISO-8859-1"))

buffer = []

while True:
    d = s.recv(256)
    if not d:
        break
    buffer.append(d)

s.close()
response = b"".join(buffer).decode("ISO-8859-1")
print(response)
