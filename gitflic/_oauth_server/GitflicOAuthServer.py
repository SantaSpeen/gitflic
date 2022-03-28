import http.server
import json
import os
import sys
from typing import Tuple, AnyStr, NoReturn
from urllib.parse import parse_qs, urlsplit
import importlib.resources
from random import randint

import requests

from gitflic import __version__

_debug = False
server: http.server.HTTPServer
redirect_link: str
_GitflicAuth: object


class GitflicOAuthServer(http.server.BaseHTTPRequestHandler):
    server_version = f"GitflicOAuthServer/{__version__}"
    default_request_version = "HTTP/1.0"

    @staticmethod
    def get_html() -> str:
        """ Get HTML page from module """
        with importlib.resources.open_text("gitflic._oauth_server", "page.html") as f:
            html = f.read()
        return html

    def send_html_row(self, what: AnyStr, description: AnyStr, data: str) -> NoReturn:
        """ Add row at page using Bootstrap CSS  """
        html = f"""
        <!-- {what} -->
        <div class="row">
            <div class="col-sm-2 сol-md-2">{description}</div>
            <div class="col-md-1"> -> </div>
            <div class="col-md-9"><code>{data}</code></div>
        </div>
        """
        self.send(html)

    def send_html_error(self, reason) -> NoReturn:
        """ Add error info at page using Bootstrap CSS  """
        error_html = f"""
        <br/><br/>
        <!-- Error -->
        <dev class="text-center lh-1">
            <p class="text-danger fs-1">Error!</p>
            <p class="text-muted fs-3">{reason}</p>
        </div>
        """
        self.send(error_html)

    def send_headers(self, code: int) -> None:
        self.send_response(code)
        self.send_header("Content-type", "text/html; charset=UTF-8")
        self.end_headers()

    def send(self, html: str) -> NoReturn:
        """ wfile.write handler """
        self.wfile.write(bytes(html, "UTF-8"))

    # noinspection PyPep8Naming
    def do_GET(self) -> NoReturn:
        """ GET request handler """
        is_error = False
        url = urlsplit(self.path)
        params = parse_qs(url.query)
        code = state = None

        if url.path != "/":
            # Allow only root path ;)
            self.send_headers(404)
            self.send(f'''
                <head><title>Not found</title></head>
                <div align="center">
                    <h1>Erorr 404</h1>
                    <span>Cannot find: {url.path}</span>
                </div>
                <hr/>
                <center>
                    {self.server_version.replace("/", " ")} by <a href="https://github.com/SantaSpeen">SantaSpeen</a>
                </center>''')
        else:
            for k, v in params.items():
                if k == "code":
                    code = v[0]
                elif k == "state":
                    state = v[0]
            self.send_headers(200 if code else 500)
            try:
                html_page = self.get_html()
                html_page %= {"head_tag": "", "code": code, "state": state}

                # Send beginning HTML page
                self.send(html_page)

                if code:
                    config_path = os.path.join(os.getcwd(), "config.json")

                    # Send config_path
                    self.send_html_row("config_path", "Config path:", config_path)

                    res = requests.get("https://oauth.gitflic.ru/api/token/access?code=" + code)
                    if res.status_code == 200:
                        jsn = {"request": {"code": code, "state": state}, "response": res.json()}
                        with open(os.path.join(os.getcwd(), "config.json"), "w") as f:
                            json.dump(jsn, f, indent=3)

                        access_token = jsn['response']['accessToken']
                        if _GitflicAuth:
                            _GitflicAuth.access_token = access_token
                            _GitflicAuth.refresh_token = jsn['response']['refreshToken']
                        self.send_html_row("access_token", "Access Token:", access_token)
                    else:
                        is_error = True
                        error = None
                        title_split = res.json()['title'].split(".")
                        if len(title_split) == 6:
                            error = title_split[2].title() + " " + title_split[3].title() + " - " + title_split[4]
                        self.send_html_error(f"GitFlic api send: {error or 'Unknown error'}")
                else:
                    is_error = True
                    self.send_html_error("Code is none. Cannot auth.")

            except Exception as e:
                is_error = True
                print(f"GitflicOAuthServer Error: {e!r}")
                self.send_html_error(f"GitflicOAuthServer Error: {e!r}")  # This not always sends...

            # Info and footer send
            self.send("""
            <div style="min-height: 53vh !important;"> </div>
            <div class="text-center bg-light mt-auto container-fluid">
                <div class="text-muted lh-1">
                    <p class="fs-2">Server close automatically.</p>
                    <p class="fs-">You can close this page</p>
                </div>
                <div class="p-1">
                    Copyright:
                    <a class="text-dark" href="https://github.com/SantaSpeen/gitflic/"> © GitFlic python lib</a>.<br/>
                    Icons and logo Copyright:
                    <a class="text-dark" href="https://gitflic.ru/"> © GitFlic</a>.
                </div>
            </div>
            """)

            # Close unclosed tags
            self.send("""
            <!-- Close html tag line 52: <div class="container-fluid"> -->
            </div> 
            """)

            if not _debug:
                sys.stdout.write("GitflicOAuthServer closed.\n")
                server.server_close()
                if is_error:
                    sys.stderr.write("GitflicOAuthServer send error.\n")
                sys.exit(1)


def get_server(auth_class, port: int = None) -> Tuple[http.server.HTTPServer, str, str]:
    global server, redirect_link, _GitflicAuth
    _GitflicAuth = auth_class
    url = "https://gitflic.santaspeen.ru/"
    try:
        port = port or randint(49152, 65535)
        server_address = ('localhost', port)
        req = requests.get(url+"getstate", params={"port": port})
        if req.status_code == 201:
            server = http.server.HTTPServer(server_address, GitflicOAuthServer)
            serving = f"http://{':'.join([str(i) for i in server_address])}/"
            print(f"GitflicOAuthServer serving on {serving}")
            state = req.json()['state']
            return server, url+state, state
    except Exception as e:
        print(f"get_server send error: {e}. Trying to rebind server.")
        return get_server(auth_class)

    raise Exception(f"Cannot get state code from {url}")


def kill_server():
    exit(0)


if __name__ == '__main__':
    _debug = True
    get_server(GitflicOAuthServer, 11491)
    try:
        # noinspection PyUnboundLocalVariable
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
