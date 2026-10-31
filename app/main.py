import argparse
import os
import socket  # noqa: F401
from threading import Thread


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

def handle_request(conn, root_path):
    data = conn.recv(1024)
    decoded_data = data.decode()
    request_line, headers, request_body = structure(decoded_data)
    request_target = request_line.split()[1]
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
        user_agent = headers.get("User-Agent")
        content_length = len(user_agent)
        response = (
            f"HTTP/1.1 200 OK\r\n" +
            f"Content-Type: text/plain\r\n" +
            f"Content-Length: {content_length}\r\n\r\n" +
            f"{user_agent}"
        )
        conn.sendall(response.encode())
    elif request_target.split("/")[1] == "files":
        file_path = os.path.join(root_path, request_target.split("/")[2])
        try:
            file_obj = open(file_path)
            file_contents = file_obj.read()
            content_length = len(file_contents)
            response = (
                f"HTTP/1.1 200 OK\r\n" +
                f"Content-Type: octet-stream\r\n" +
                f"Content-Length: {content_length}\r\n\r\n" +
                f"{file_contents}"
            )
            conn.sendall(response.encode())
        except OSError as e:
            conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

    else:
        conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
    conn.close()

def main():
    print("Logs from your program will appear here!")
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory')
    args = parser.parse_args()
    root_path = args.directory

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        conn, address = server_socket.accept() # wait for client
        Thread(target=handle_request, args=(conn,root_path)).start()

if __name__ == "__main__":
    main()
