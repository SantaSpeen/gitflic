"""
Gitflic authentication wrapper.
"""
import json
import os
import threading
from urllib.parse import quote_plus, parse_qs, urlsplit
import webbrowser
from enum import Enum
from typing import Union
import logging

import requests

from .exceptions import AuthError, GitflicExceptions
from .__version__ import __version__
from ._oauth_server import GitflicOAuthServer

OAUTH_URL = "https://oauth.gitflic.ru/oauth/authorize?scope={}&clientId={}&redirectUrl={}&state={}"


def _add_enum_values(*args):
    string = str()
    for arg in args:
        if isinstance(arg, Enum):
            string += arg.value
        else:
            string += str(arg)
        string += ","
    return string[:len(string) - 1]


class GitflicAuthScopes(Enum):
    """ Authentication scopes from Gitflic. Doc: https://gitflic.ru/help/api/access-token"""
    USER_READ = "USER_READ"
    USER_WRITE = "USER_WRITE"
    PROJECT_READ = "PROJECT_READ"
    PROJECT_WRITE = "PROJECT_WRITE"
    PROJECT_EDIT = "PROJECT_EDIT"

    # For a hint in the IDE
    ALL_READ: "GitflicAuthScopes.ALL_READ"
    ALL_WRITE: "GitflicAuthScopes.ALL_WRITE"
    ALL: "GitflicAuthScopes.ALL"


GitflicAuthScopes.ALL_READ = _add_enum_values(GitflicAuthScopes.USER_READ,
                                              GitflicAuthScopes.PROJECT_READ)
GitflicAuthScopes.ALL_WRITE = _add_enum_values(GitflicAuthScopes.PROJECT_WRITE,
                                               GitflicAuthScopes.PROJECT_EDIT,
                                               GitflicAuthScopes.PROJECT_WRITE)
GitflicAuthScopes.ALL = _add_enum_values(GitflicAuthScopes.ALL_WRITE,
                                         GitflicAuthScopes.ALL_READ)


class GitflicAuth:
    """
    Gitflic authentication wrapper.
    """

    # noinspection PyTypeChecker
    def __init__(self,
                 access_token: str = None,
                 localhost_oauth: bool = False,
                 scope: Union[GitflicAuthScopes, str] = GitflicAuthScopes.ALL_READ,
                 client_id: str = "cc2a5d8a-385a-4367-8b2b-bb2412eacb73",
                 redirect_url: str = "https://gitflic.ru/settings/oauth/token",
                 state: str = None):
        """
        :param access_token: Raw token for raw AUTH.
        :param scope: OAUTH field. Default GitflicAuthScopes.ALL_READ
        :param client_id: OAUTH field. Default "cc2a5d8a-385a-4367-8b2b-bb2412eacb73", Simple gitflic app
        :param redirect_url: OAUTH field. Default "https://gitflic.ru/settings/oauth/token/"
        :param state: OAUTH field. Default "python_user"
        """

        # Logging.
        self.log: logging.Logger = logging.getLogger(__name__)

        # Requests.
        self.session: requests.Session = requests.Session()

        # Set headers
        self.session.headers = {
            "User-Agent": f"gitflic-py/{__version__}",
            'Accept': "application/*",
            'Authorization': "token "
        }

        # Token fields.
        self.access_token: str = access_token
        self.refresh_token: str = None

        # OAUTH fields.
        self.scope: str = scope if not isinstance(scope, GitflicAuthScopes) else scope.value
        self._localhost_oauth: bool = localhost_oauth

        self.client_id: str = client_id
        self.redirect_url: str = redirect_url
        self.state: str = state

        self._server_thread: threading.Thread = None

        self._try_login()

    def _try_login(self):
        """
        Tries to login user with token or OAUTH.
        """
        if self._localhost_oauth:
            self.state = self.state or "GitflicOAuthServer"
            if not (self.scope and self.client_id):
                raise GitflicExceptions(
                    "Using localhost, you are required to this params: ('scope', 'client_id')! "
                )
            self._oauth_login()
        elif self.access_token:
            # Raw authorization.
            self._token_login()
        else:
            if self.scope and self.client_id and self.state:
                # OAUTH authorization.
                self._oauth_login()
            else:
                if any((self.scope, self.client_id, self.redirect_url, self.state)):
                    raise GitflicExceptions(
                        "Not found one or more of params for OAUTH, you are required to send ALL params from ('scope', 'client_id', 'redirect_url', 'state')! "
                        "See docs: https://gitflic.ru/help/api/access-token."
                    )
                raise GitflicExceptions(
                    "Please pass 'token' param for raw auth or ('scope', 'client_id', 'redirect_url', 'state') params for OAUTH "
                    "See docs: https://gitflic.ru/help/api/access-token."
                )

    def _oauth_login(self):
        """
        Tries to login user with OAUTH.
        """

        self.log.debug("Trying to login with OAUTH...")

        if self._localhost_oauth:
            server, self.redirect_url, self.state = GitflicOAuthServer.get_server(self)

        # OAUTH authorization.
        redirect_url = quote_plus(self.redirect_url)
        webbrowser.open(OAUTH_URL.format(self.scope, self.client_id, redirect_url, self.state))
        if not self._localhost_oauth:
            code = input("Paste code: ")
            if not code:
                raise AuthError("Cannot find code.")
            res = self.session.get("https://oauth.gitflic.ru/api/token/access?code=" + code)
            if res.status_code == 200:
                res = res.json()
                jsn = {"request": {"code": code, "state": None}, "response": res}
                with open(os.path.join(os.getcwd(), "config.json"), "w") as f:
                    json.dump(jsn, f, indent=3)
                access_token = res['accessToken']
                self.access_token = access_token
                self.refresh_token = res['refreshToken']
                self.session.headers["Authorization"] += access_token
            else:
                error = None
                title_split = res.json()['title'].split(".")
                if len(title_split) == 6:
                    error = title_split[2].title() + " " + title_split[3].title() + ": " + title_split[4]
                raise AuthError(error or "Unknown error")
        else:
            self._server_thread = threading.Thread(target=server.serve_forever)
            self._server_thread.start()
            print("Waiting server..")
            self._server_thread.join()

        self.session.headers['Authorization'] += self.access_token
        self.check_token()

    def _token_login(self):
        """
        Tries to login user with given access token.
        """

        self.log.debug(f"Trying to login with token={self.access_token}...")

        assert isinstance(self.access_token, str)
        self.session.headers['Authorization'] += self.access_token

        self.check_token()

    def check_token(self):
        """
        Checks that current auth session token is valid or not (by making request to get current user).
        """

        self.log.debug("Checking token....")
        r = self.session.get("https://api.gitflic.ru/user/me")

        if r.status_code == 403:
            e = AuthError("Authentication failed. Invalid token?")
            e.response = r
            raise e
        else:
            r = r.json()
            self.log.debug(f"Successfully logged as {r.get('username')} {r.get('id')}")
