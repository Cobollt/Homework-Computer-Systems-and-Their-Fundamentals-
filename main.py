import json
import mimetypes
import os
import socket
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from multiprocessing import Process
from pathlib import Path
from urllib.parse import parse_qs

from pymongo import MongoClient
from pymongo.errors import PyMongoError


BASE_DIR = Path(__file__).parent

HTTP_HOST = "0.0.0.0"
HTTP_PORT = 3000

SOCKET_HOST = "0.0.0.0"
SOCKET_PORT = 5000

MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb://mongo:27017"
)

MONGO_DB = "messages_db"
MONGO_COLLECTION = "messages"


class HttpHandler(BaseHTTPRequestHandler):
    def send_file(self, file_name, status=200):
        file_path = BASE_DIR / file_name

        try:
            content = file_path.read_bytes()

            content_type, _ = mimetypes.guess_type(
                file_path
            )

            self.send_response(status)
            self.send_header(
                "Content-Type",
                content_type
                or "application/octet-stream"
            )
            self.send_header(
                "Content-Length",
                str(len(content))
            )
            self.end_headers()

            self.wfile.write(content)

        except OSError:
            self.send_error_page()

    def send_error_page(self):
        file_path = BASE_DIR / "error.html"

        try:
            content = file_path.read_bytes()

            self.send_response(404)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            self.send_header(
                "Content-Length",
                str(len(content))
            )
            self.end_headers()

            self.wfile.write(content)

        except OSError:
            self.send_error(
                404,
                "Not Found"
            )

    def do_GET(self):
        routes = {
            "/": "index.html",
            "/index.html": "index.html",
            "/message.html": "message.html",
            "/style.css": "style.css",
            "/logo.png": "logo.png"
        }

        file_name = routes.get(
            self.path
        )

        if file_name:
            self.send_file(
                file_name
            )
        else:
            self.send_error_page()

    def do_POST(self):
        if self.path != "/message":
            self.send_error_page()
            return

        try:
            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(
                content_length
            ).decode("utf-8")

            form_data = parse_qs(body)

            data = {
                "username": form_data.get(
                    "username",
                    [""]
                )[0],
                "message": form_data.get(
                    "message",
                    [""]
                )[0]
            }

            send_to_socket_server(
                data
            )

            self.send_response(303)
            self.send_header(
                "Location",
                "/message.html"
            )
            self.end_headers()

        except Exception as error:
            print(
                f"HTTP error: {error}"
            )
            self.send_error_page()


def send_to_socket_server(data):
    message = json.dumps(
        data
    ).encode("utf-8")

    with socket.create_connection(
        ("127.0.0.1", SOCKET_PORT),
        timeout=5
    ) as client:
        client.sendall(message)
        client.shutdown(
            socket.SHUT_WR
        )


def save_to_mongodb(
    collection,
    data
):
    document = {
        "date": str(
            datetime.now()
        ),
        "username": data.get(
            "username",
            ""
        ),
        "message": data.get(
            "message",
            ""
        )
    }

    collection.insert_one(
        document
    )

    print(
        f"Saved: {document}"
    )


def run_socket_server():
    client = MongoClient(
        MONGO_URL,
        serverSelectionTimeoutMS=5000
    )

    database = client[
        MONGO_DB
    ]

    collection = database[
        MONGO_COLLECTION
    ]

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(
        (
            SOCKET_HOST,
            SOCKET_PORT
        )
    )

    server.listen()

    print(
        f"Socket server running "
        f"on port {SOCKET_PORT}"
    )

    while True:
        connection, address = (
            server.accept()
        )

        with connection:
            try:
                data = b""

                while True:
                    chunk = (
                        connection.recv(
                            4096
                        )
                    )

                    if not chunk:
                        break

                    data += chunk

                message = json.loads(
                    data.decode(
                        "utf-8"
                    )
                )

                save_to_mongodb(
                    collection,
                    message
                )

            except (
                json.JSONDecodeError,
                UnicodeDecodeError,
                PyMongoError
            ) as error:
                print(
                    f"Socket error: {error}"
                )


def run_http_server():
    server = ThreadingHTTPServer(
        (
            HTTP_HOST,
            HTTP_PORT
        ),
        HttpHandler
    )

    print(
        f"HTTP server running "
        f"on port {HTTP_PORT}"
    )

    server.serve_forever()


def main():
    socket_process = Process(
        target=run_socket_server
    )

    http_process = Process(
        target=run_http_server
    )

    socket_process.start()
    http_process.start()

    socket_process.join()
    http_process.join()


if __name__ == "__main__":
    main()