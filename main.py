from http.server import HTTPServer

from components.http.handler import RequestHandler


def run():
    port = 8008
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print("start.....")
    httpd.serve_forever()


if __name__ == '__main__':
    run()