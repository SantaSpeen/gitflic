from enum import Enum
import logging
from typing import Union
import webbrowser
import urllib.parse

import requests

from .exceptions import AuthError, GitflicExceptions

oauth_url = "https://oauth.gitflic.ru/oauth/authorize?scope={}&clientId={}&redirectUrl={}&state={}"


class GitflicAuthScopes(Enum):
    USER_READ = "USER_READ"
    USER_WRITE = "USER_WRITE"
    PROJECT_READ = "PROJECT_READ"
    PROJECT_WRITE = "PROJECT_WRITE"
    PROJECT_EDIT = "PROJECT_EDIT"

    ALL = "USER_READ,USER_WRITE,PROJECT_READ,PROJECT_WRITE,PROJECT_EDIT"


class GitflicAuth:

    # noinspection PyTypeChecker
    def __init__(self,
                 access_token: str = None,
                 scope: Union[GitflicAuthScopes, str] = None,
                 client_id: str = None,
                 redirect_url: str = None,
                 state: str = None):
        """

        :param access_token:
        :param scope:
        :param client_id:
        :param redirect_url:
        """

        self.log: logging.Logger = logging.getLogger(__name__)

        self.session: requests.Session = requests.Session()

        self.access_token: str = access_token

        self.scope: str = scope if not isinstance(scope, GitflicAuthScopes) else scope.value
        self.client_id: str = client_id
        self.redirect_url: str = redirect_url
        self.state = state

        self.refresh_token: str = None

        if any((access_token, scope, client_id, redirect_url, state)):
            if access_token:
                pass
            elif not (scope and client_id and redirect_url, state):
                raise GitflicExceptions(
                    "Cannot auth without 'scope', 'client_id', 'redirect_url', 'state' parameters. "
                    "See doc: https://gitflic.ru/help/api/access-token."
                )
        else:
            raise GitflicExceptions(
                "Cannot auth without 'token' or 'scope' and 'client_id' and 'redirect_url' and 'state' parameters. "
                "See doc: https://gitflic.ru/help/api/access-token."
            )

        self._login()

    def _login(self):
        self.log.debug("Trying to login.")

        if self.access_token:
            self.session.headers.update({"Authorization": "token " + self.access_token})
        else:

            raise GitflicExceptions("Oauth not ready. Use access_token.")

            # redirect_url = urllib.parse.quote_plus(self.redirect_url)
            # webbrowser.open(oauth_url.format(self.scope, self.client_id, redirect_url, self.state))
            # url = input("Paste redirect url: ")
            # r = self.session.get("").json()
            # print(r)

            # self.session.headers.update({"Authorization": "token " + "null"})

        self.check_token()

    def check_token(self):
        self.log.debug("Check token.")
        r = self.session.get("https://api.gitflic.ru/user/me")

        if r.status_code == 403:
            raise AuthError("Authentication failed.")
        else:
            r = r.json()
            self.log.debug(f"Logged as {r.get('username')} {r.get('id')}")
