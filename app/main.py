import socket  # noqa: F401


def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    conn, address = server_socket.accept() # wait for client
    conn.sendall("HTTP/1.1 200 OK\r\n\r\n".encode())


if __name__ == "__main__":
    main()
