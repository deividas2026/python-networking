import json

def send_response(connection, status, message=""):
    status_messages = {
        400: "Bad Request",
        200: "OK",
        408: "Request Timeout",
        411: "Length Required"
    }

    if status == 200:
        payload = b'{"message":"Hello from server"}'
    elif status >= 400 or status < 500:
        payload = {
            "error": f"{status_messages.get(status)}",
            "message": message
        } 
        payload = json.dumps(payload).encode("ISO-8859-1")

    response = (
        f"HTTP/1.1 {status} {status_messages.get(status)}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(payload)}\r\n"
        "\r\n"
    ).encode("ISO-8859-1")
    response += payload

    connection.sendall(response)
    connection.close()
