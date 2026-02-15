import base64
import socket
import hashlib
import json
import threading 
import os
from watch import start_watcher

websocket_clients = []

def send_reload(filename):
    for client in websocket_clients:
        try:
            send_ws_message(client, "reload")
        except:
            websocket_clients.remove(client) 
    

def main():
    threading.Thread(
        target=start_watcher,
        args=(["index.html"], send_reload),
    ).start()
    start_server()

    
def start_server():
    PORT = 28333
    HOST = "localhost"

    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        handle_connection(client_socket, client_address)


def handle_connection(client_socket, client_address):
    print("-----------------------------------------------")
    print(f"New connection: {client_address}")

    buffer = b""
    while True:
        data = client_socket.recv(1024)
        if not data:
            client_socket.close()
            return
        buffer += data
        if b"\r\n\r\n" in buffer:
            break
        
    header = data.split(b"\r\n\r\n")[0].decode()
    header_fields = {}
    for header_field in header.split("\r\n")[1:]:
        key, value = header_field.split(":", 1)
        header_fields[key.strip().lower()] = value.strip()
          
    if (
        "connection" in header_fields
        and header_fields["connection"].lower() == "upgrade"
        and "upgrade" in header_fields
        and header_fields["upgrade"].lower() == "websocket"
    ):
        # send switchin protocols
        print("This is a websocket request")
        print(json.dumps(header_fields, indent=4))

        sec_websocket_key = header_fields["sec-websocket-key"] 
        handshake_response = get_handshake_response(sec_websocket_key)
        client_socket.sendall(handshake_response.encode())
        websocket_clients.append(client_socket)
        return

    html = inject_reload_script("index.html")
    html = html.encode()
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html\r\n"
        f"Content-Length: {len(html)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode() 
    response += html
    client_socket.sendall(response)
    client_socket.close()

    
def inject_reload_script(filename):
    with open(filename) as file:
        html = file.read()

    script = """
    <script>
        const socket = new WebSocket("ws://localhost:28333");
        socket.addEventListener("message", (event) => {
            location.reload()
        });
    </script>
    """
    
    return html.replace("</body>", script + "\n</body>")


def get_handshake_response(key):
    magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    accept_key = base64.b64encode(hashlib.sha1((key + magic_string).encode()).digest()    ).decode()

    return (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept_key}\r\n"
        "\r\n"
    )


def send_ws_message(client_socket, message):
    payload = message.encode()
    length = len(payload)
    frame = bytearray()
    frame.append(0x81)
    frame.append(length)
    frame.extend(payload)
    client_socket.sendall(frame)


if __name__ == "__main__":
    main()
