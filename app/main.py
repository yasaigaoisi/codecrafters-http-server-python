import socket  # noqa: F401


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, address = server_socket.accept() # wait for client
    data = conn.recv(1024)
    decoded_data = data.decode()
    request_line = decoded_data.splitlines()[0]
    request_target = request_line.split()[1]
    user_agent = decoded_data.splitlines()[3].split()[1]
    if request_target == "/":
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


if __name__ == "__main__":
    main()
