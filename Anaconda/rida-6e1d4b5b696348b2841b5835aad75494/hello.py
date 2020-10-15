#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from argparse import ArgumentParser
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from http import HTTPStatus


class HelloHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Hello Anaconda Enterprise!')
        return


def runserver(address, port):
    server_address = (address, int(port))
    httpd = HTTPServer(server_address, HelloHandler)
    try:
        print("Server available at {}:{}".format(address, port))
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server")
        httpd.socket.close()


# Arg parser for the anaconda-project http options
parser = ArgumentParser(prog="Hello Anaconda Enterprise", description="Minimal Anaconda Enteprise deployable example")
parser.add_argument('--anaconda-project-host', action='append', help='Hostname to allow in requests')
parser.add_argument('--anaconda-project-no-browser', action='store_true', default=False, help='Disable opening in a browser')
parser.add_argument('--anaconda-project-use-xheaders', action='store_true', default=False, help='Trust X-headers from reverse proxy')
parser.add_argument('--anaconda-project-url-prefix', action='store', default='', help='Prefix in front of urls')
parser.add_argument('--anaconda-project-port', action='store', default='8484', help='Port to listen on')
parser.add_argument('--anaconda-project-iframe-hosts', action='append', help='Space-separated hosts which can embed us in an iframe per our Content-Security-Policy')
parser.add_argument('--anaconda-project-address', action='store', default='0.0.0.0', help='IP address the application should listen on.')


if __name__ == '__main__':
    # This app accepts all anaconda-project http options, but ignores most of them.
    args = parser.parse_args(sys.argv[1:])
    runserver(address=args.anaconda_project_address, port=args.anaconda_project_port)
