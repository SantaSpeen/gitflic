import http.server
import json
import os
import sys
from typing import Tuple, AnyStr, NoReturn
from urllib.parse import parse_qs, urlsplit
from random import randint

import requests

from gitflic import __version__

_debug = False
server: http.server.HTTPServer
redirect_link: str
_GitflicAuth: object


def get_html():
    return """
    <!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- BootStrap CSS 5.1.3 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    <title>Gitflic OAuth</title>
    <!--  GitFlic icons  -->
    <link rel="icon" type="image/png" href="https://gitflic.ru/static/image/favicon/android-icon-192x192.png">
    <link rel="apple-touch-icon" sizes="57x57" href="https://gitflic.ru/static/image/favicon/apple-icon-57x57.png">
    <link rel="apple-touch-icon" sizes="60x60" href="https://gitflic.ru/static/image/favicon/apple-icon-60x60.png">
    <link rel="apple-touch-icon" sizes="72x72" href="https://gitflic.ru/static/image/favicon/apple-icon-72x72.png">
    <link rel="apple-touch-icon" sizes="76x76" href="https://gitflic.ru/static/image/favicon/apple-icon-76x76.png">
    <link rel="apple-touch-icon" sizes="114x114" href="https://gitflic.ru/static/image/favicon/apple-icon-114x114.png">
    <link rel="apple-touch-icon" sizes="120x120" href="https://gitflic.ru/static/image/favicon/apple-icon-120x120.png">
    <link rel="apple-touch-icon" sizes="144x144" href="https://gitflic.ru/static/image/favicon/apple-icon-144x144.png">
    <link rel="apple-touch-icon" sizes="152x152" href="https://gitflic.ru/static/image/favicon/apple-icon-152x152.png">
    <link rel="apple-touch-icon" sizes="180x180" href="https://gitflic.ru/static/image/favicon/apple-icon-180x180.png">
    <link rel="icon" type="image/png" sizes="192x192" href="https://gitflic.ru/static/image/favicon/android-icon-192x192.png">
    <link rel="icon" type="image/png" sizes="32x32" href="https://gitflic.ru/static/image/favicon/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="96x96" href="https://gitflic.ru/static/image/favicon/favicon-96x96.png">
    <link rel="icon" type="image/png" sizes="16x16" href="https://gitflic.ru/static/image/favicon/favicon-16x16.png">
    %(head_tag)s
</head>
<body>
    <div class="container-fluid">
        <header class="shadow">
            <div class="row">
                <!--  GitFlic logo  -->
                <div class="col-sm-1 img-fluid" style="padding-top: 6px">
                    <a href="https://gitflic.ru/">
                        <svg xmlns="http://www.w3.org/2000/svg" width="211" height="70" viewBox="0 0 211 70">
                        <path d="M60 33.9602C60 28.6904 58.3294 23.7987 55.4907 19.7814C57.0561 18.2099 58.0374 16.0358 58.0374 13.6373C58.0374 8.86373 54.2173 5 49.4977 5C46.028 5 43.0374 7.10319 41.7056 10.1162C39.5678 9.5254 37.3248 9.2182 35 9.2182C32.6869 9.2182 30.4439 9.5254 28.3178 10.1162C26.986 7.10319 23.9953 5.01182 20.5257 5.01182C15.8061 5.01182 11.986 8.87554 11.986 13.6491C11.986 16.0477 12.9556 18.2217 14.521 19.7814C11.6706 23.7987 10 28.6904 10 33.972C10 40.4943 12.5584 46.4376 16.729 50.8566L16.7523 50.8803C17.278 51.4356 17.8388 51.9791 18.4229 52.4872L27.7804 61.5144L29.9883 59.3403L34.8832 65L39.8949 59.2103L42.2313 61.5026L51.6122 52.4636C52.1729 51.9673 52.7103 51.4474 53.2243 50.9039L53.271 50.8566C57.4416 46.4258 60 40.4825 60 33.9602ZM24.1472 25.7129C23.7617 25.2166 23.6565 24.6967 23.7734 24.2596C23.8902 23.8224 24.2407 23.4325 24.8248 23.1961C25.4089 22.9598 26.1799 22.8889 26.986 23.1134C27.7921 23.3379 28.4346 23.7751 28.8201 24.2832C29.1939 24.7794 29.2991 25.2993 29.1822 25.7365C29.0654 26.1737 28.715 26.5636 28.1425 26.7999C27.5584 27.0362 26.7874 27.1071 25.9813 26.8826C25.1752 26.6581 24.5327 26.221 24.1472 25.7129ZM41.4252 40.3643C40.1752 40.9905 38.7033 41.3568 37.6285 42.0185C37.2547 42.243 36.9159 42.503 36.6122 42.822C36.3318 43.1056 35.3855 44.1808 35.8878 45.6577C36.4019 47.1701 38.0491 48.1981 39.9299 48.2217C40.222 48.2217 40.4556 48.4699 40.4439 48.7653C40.4439 49.0607 40.2103 49.2852 39.9182 49.2852C39.9182 49.2852 39.9182 49.2852 39.9065 49.2852C37.6869 49.2497 35.736 48.0445 34.9766 46.2485C34.2523 48.1154 32.2664 49.3797 30 49.4033C30 49.4033 30 49.4033 29.9883 49.4033C29.6963 49.4033 29.4626 49.167 29.4626 48.8834C29.4626 48.588 29.6963 48.3517 29.9766 48.3399C31.8575 48.3163 33.4813 47.2883 34.0187 45.7759C34.2757 45.0551 34.2523 44.0154 33.1308 42.822C32.8271 42.503 32.4766 42.243 32.1028 42.0185C31.028 41.3568 29.3692 41.0614 28.2827 40.3525C27.2664 39.549 26.6589 38.5565 26.6589 37.4813C26.6589 37.4222 26.6589 37.3513 26.6706 37.2922C26.8341 34.7164 30.4322 32.6605 34.8481 32.6605C39.1822 32.6605 42.722 34.6337 43.014 37.1386C43.0257 37.245 43.0374 37.3631 43.0374 37.4813C43.0491 38.5683 42.4299 39.8562 41.4252 40.3643ZM45.9813 25.7247C45.5958 26.221 44.965 26.67 44.1472 26.8944C43.3411 27.1189 42.5701 27.0481 41.986 26.8117C41.4019 26.5754 41.0514 26.1855 40.9346 25.7483C40.8178 25.3111 40.9229 24.7913 41.3084 24.295C41.6939 23.7987 42.3248 23.3497 43.1425 23.1252C43.9486 22.9007 44.7196 22.9716 45.3037 23.208C45.8879 23.4443 46.2383 23.8342 46.3551 24.2714C46.472 24.7085 46.3668 25.2284 45.9813 25.7247Z" fill="black"/>
                        <path d="M96.84 30.1061H102.903C101.892 23.6431 96.3107 19.1415 89.0449 19.1415C80.4478 19.1415 74 25.4759 74 36.0868C74 46.5048 80.1591 52.9678 89.2213 52.9678C97.3533 52.9678 103.176 47.7267 103.176 39.2379V35.283H89.8469V39.9453H97.4174C97.3212 44.6399 94.1935 47.6142 89.2534 47.6142C83.7519 47.6142 79.9827 43.4823 79.9827 36.0225C79.9827 28.6109 83.8161 24.4952 89.1251 24.4952C93.0868 24.4952 95.7814 26.6174 96.84 30.1061Z" fill="black"/>
                        <path d="M110.217 52.5177H116.023V27.8232H110.217V52.5177ZM113.136 24.3183C114.981 24.3183 116.488 22.9035 116.488 21.1672C116.488 19.4148 114.981 18 113.136 18C111.275 18 109.768 19.4148 109.768 21.1672C109.768 22.9035 111.275 24.3183 113.136 24.3183Z" fill="black"/>
                        <path d="M134.296 27.8232H129.436V21.9068H123.63V27.8232H120.133V32.3248H123.63V46.0547C123.598 50.701 126.966 52.9839 131.329 52.8553C132.981 52.8071 134.119 52.4855 134.745 52.2765L133.767 47.7267C133.446 47.8071 132.788 47.9518 132.066 47.9518C130.607 47.9518 129.436 47.4373 129.436 45.09V32.3248H134.296V27.8232Z" fill="black"/>
                        <path d="M139.938 52.5177H145.888V38.5305H159.538V33.5305H145.888V24.5916H160.981V19.5916H139.938V52.5177Z" fill="black"/>
                        <path d="M171.952 19.5916H166.146V52.5177H171.952V19.5916Z" fill="black"/>
                        <path d="M177.923 52.5177H183.729V27.8232H177.923V52.5177ZM180.842 24.3183C182.687 24.3183 184.194 22.9035 184.194 21.1672C184.194 19.4148 182.687 18 180.842 18C178.981 18 177.474 19.4148 177.474 21.1672C177.474 22.9035 178.981 24.3183 180.842 24.3183Z" fill="black"/>
                        <path d="M200.446 53C206.637 53 210.583 49.3183 211 44.0772H205.45C204.953 46.7299 203.044 48.2572 200.494 48.2572C196.869 48.2572 194.528 45.2187 194.528 40.1704C194.528 35.1865 196.917 32.1961 200.494 32.1961C203.285 32.1961 205.001 33.9968 205.45 36.3762H211C210.599 31.0225 206.429 27.5016 200.414 27.5016C193.196 27.5016 188.641 32.7267 188.641 40.2669C188.641 47.7428 193.084 53 200.446 53Z" fill="black"/>
                        </svg>
                    </a>
                </div>
                <div class="col-sm-10 lh-1 text-center">
                    <p class="text-muted fs-2" style="padding-top: 9px">OAuth</p>
                    <p class="fs-6 fw-light">localhost server</p>
                </div>
            </div>
        </header>
    </div>
    <div class="container">
        <br/>
        <div class="row">
            <div class="col-sm-2 col-md-2">Code</div>
            <div class="col-md-1">-></div>
            <div class="col-md-9"><code>%(code)s</code></div>
        </div>
        <div class="row">
            <div class="col-sm-2 col-md-2">State</div>
            <div class="col-md-1">-></div>
            <div class="col-md-9"><code>%(state)s</code></div>
        </div>
        <!-- Next html generate in python server -->
</body>
</html>
    """


class GitflicOAuthServer(http.server.BaseHTTPRequestHandler):
    server_version = f"GitflicOAuthServer/{__version__}"
    default_request_version = "HTTP/1.0"

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
                html_page = get_html()
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
