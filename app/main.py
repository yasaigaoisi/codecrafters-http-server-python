import socket  # noqa: F401


def structure(data: str):
    splitted_data = data.split("\r\n\r\n")
    if len(splitted_data) == 1:
        etc = splitted_data[0]
        request_body = ''
    else:
        etc, request_body = data.split("\r\n\r\n")
    request_line, headers_array = etc.split("\r\n")[0], etc.split("\r\n")[1:]
    headers = {}
    for header in headers_array:
        key, value = header.split()
        headers[key.split(":")[0]] = value

    return (
        request_line,
        headers,
        request_body
    )

def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        conn, address = server_socket.accept() # wait for client
        # with conn:
        data = conn.recv(1024)

        decoded_data = data.decode()
        request_line, headers, request_body = structure(decoded_data)
        request_target = request_line.split()[1]
        printf(request_target)
        if request_target == "/":
            printf("root request")
            conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        elif request_target.split("/")[1] == "echo":
            echo_target = request_target.split("/")[2]
            content_length = len(echo_target)
            response = (
                f"HTTP/1.1 200 OK\r\n" +
                f"Content-Type: text/plain\r\n" +
                f"Content-Length: {content_length}\r\n\r\n" +
                f"{echo_target}"
            )
            conn.sendall(response.encode())
        elif request_target.split("/")[1] == "user-agent":
            user_agent = headers.get("User-Agent")
            content_length = len(user_agent)
            response = (
                f"HTTP/1.1 200 OK\r\n" +
                f"Content-Type: text/plain\r\n" +
                f"Content-Length: {content_length}\r\n\r\n" +
                f"{user_agent}"
            )
            conn.sendall(response.encode())
        else:
            conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
        conn.close()


if __name__ == "__main__":
    main()
