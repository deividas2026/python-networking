def send_404():
    f = open("404.html", "r")
    fb = f.read()
    f.close()
    response = (
        "HTTP/1.1 404 Not Found\r\n"    
        "Content-Type: text/html\r\n"
        f"Content-Length: {len(fb)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return (response + fb).encode("ISO-8859-1")       
