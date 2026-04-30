# demo/consumer/app.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
from c2cpo import Tier1
from c2cpo.exceptions import C2CPOFormatViolationError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

tier1_decoder = Tier1("demo-consumer")


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        raw_request_str = post_data.decode('utf-8')

        try:
            payload = json.loads(raw_request_str)
            logging.info(f"Received payload: {payload}")

            # C2CPO decoding — fails closed on FORMAT_VIOLATION
            decoded = tier1_decoder.decode(
                payload,
                raw_request_str=raw_request_str,
                source_ip=self.client_address[0],
            )

            logging.info(f"✓ Accepted and decoded: {decoded}")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "decoded": decoded}).encode('utf-8'))

        except C2CPOFormatViolationError as e:
            logging.error(f"✗ BLOCKED (FORMAT_VIOLATION): {str(e)}")
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'')

        except Exception as e:
            logging.error(f"ERROR: {str(e)}")
            self.send_response(500)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress default HTTP server logging


def run(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    logging.info(f"C2CPO Demo Consumer listening on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
