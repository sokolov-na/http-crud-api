import json
import socketserver
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Final

PORT: Final = 9000


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        match self.path:
            case "/health":
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                data = {"status": "ok"}
                self.wfile.write(json.dumps(data).encode())
            case _:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
                self.wfile.write(b"NOT FOUND")


def run_server() -> None:
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
