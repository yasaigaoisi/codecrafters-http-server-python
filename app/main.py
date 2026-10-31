import argparse
import gzip
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
        key, value = header.split(": ")
        headers[key.split(":")[0]] = value

    return (
        request_line,
        headers,
        request_body
    )

def handle_request(conn, root_path):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            decoded_data = data.decode()
            request_line, request_headers, request_body = structure(decoded_data)
            request_method, request_target, protocol = request_line.split()


            if request_target == "/":
                response_line = "HTTP/1.1 200 OK"
                response_headers = ""
                response_body = ""
            elif request_target.split("/")[1] == "echo":
                response_line = "HTTP/1.1 200 OK"
                response_headers = "Content-Type: text/plain\r\n"
                response_body = request_target.split("/")[2]
                if request_headers.get("Accept-Encoding") and \
                    ("gzip" in request_headers.get("Accept-Encoding")):
                    response_body = gzip.compress(response_body.encode())
                    content_length = len(response_body)
                    response_headers += (
                        response_headers +
                        "Content-Encoding: gzip\r\n" +
                        f"Content-Length: {content_length}\r\n"
                    )
                else:
                    content_length = len(response_body)
                    response_headers += (
                        response_headers +
                        f"Content-Length: {content_length}\r\n"
                    )
            elif request_target.split("/")[1] == "user-agent":
                response_line = "HTTP/1.1 200 OK"
                response_body = request_headers.get("User-Agent")
                content_length = len(response_body)
                response_headers = (
                    "Content-Type: text/plain\r\n" +
                    f"Content-Length: {content_length}\r\n\r\n"
                )
            elif request_target.split("/")[1] == "files":
                file_name = request_target.split("/")[2]
                file_path = os.path.join(root_path, file_name)
                if request_method == "GET":
                    try:
                        response_line = "HTTP/1.1 200 OK"
                        file_obj = open(file_path)
                        response_body = file_obj.read()
                        content_length = len(response_body)
                        response_headers = (
                            "Content-Type: application/octet-stream\r\n" +
                            f"Content-Length: {content_length}\r\n\r\n"
                        )
                    except OSError as e:
                        response_line = "HTTP/1.1 404 Not Found"
                        response_headers = ""
                        response_body = ""
                elif request_method == "POST":
                    with open(file_path, "w") as file_obj:
                        file_obj.write(request_body)
                    response_line = "HTTP/1.1 201 Created"
                    response_headers = ""
                    response_body = ""
            else:
                response_line = "HTTP/1.1 404 Not Found"
                response_headers = ""
                response_body = ""

            if request_headers.get("Connection") == "close":
                response_headers = (
                    response_headers +
                    "Connection: close\r\n"
                )

            if request_headers.get("Accept-Encoding") and \
                ("gzip" in request_headers.get("Accept-Encoding")):
                response = (
                    (
                        f"{response_line}\r\n" +
                        f"{response_headers}\r\n"
                    ).encode() +
                    response_body
                )
            else:
                response = (
                    f"{response_line}\r\n" +
                    f"{response_headers}\r\n" +
                    response_body
                ).encode()

            conn.sendall(response)

            if request_headers.get("Connection") == "close": break

def main():
    print("Logs from your program will appear here!")
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory')
    args = parser.parse_args()
    root_path = args.directory

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    while True:
        conn, address = server_socket.accept() # wait for client
        print(conn)
        Thread(target=handle_request, args=(conn,root_path)).start()

if __name__ == "__main__":
    main()
