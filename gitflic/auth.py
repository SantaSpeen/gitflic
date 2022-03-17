"""
Gitflic authentication wrapper.
"""
from enum import Enum
from typing import Union
import logging

import requests

from .exceptions import AuthError, GitflicExceptions
from .__version__ import __version__

OAUTH_URL = "https://oauth.gitflic.ru/oauth/authorize?scope={}&clientId={}&redirectUrl={}&state={}"


class GitflicAuthScopes(Enum):
    """ Authentication scopes from Gitflic. """
    USER_READ = "USER_READ"
    USER_WRITE = "USER_WRITE"
    PROJECT_READ = "PROJECT_READ"
    PROJECT_WRITE = "PROJECT_WRITE"
    PROJECT_EDIT = "PROJECT_EDIT"

    ALL = "USER_READ,USER_WRITE,PROJECT_READ,PROJECT_WRITE,PROJECT_EDIT"


class GitflicAuth:
    """
    Gitflic authentication wrapper.
    """

    # noinspection PyTypeChecker
    def __init__(self,
                 access_token: str = None,
                 scope: Union[GitflicAuthScopes, str] = None,
                 client_id: str = None,
                 redirect_url: str = None,
                 state: str = None):
        """
        :param access_token: Raw token for raw AUTH.
        :param scope: OAUTH field.
        :param client_id: OAUTH field.
        :param redirect_url: OAUTH field.
        :param state: OAUTH field.
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

        # OAUTH fields.
        self.scope: str = scope if not isinstance(scope, GitflicAuthScopes) else scope.value
        self.client_id: str = client_id
        self.redirect_url: str = redirect_url
        self.state: str = state
        self.refresh_token: str = None

        self._try_login()

    def _try_login(self):
        """
        Tries to login user with token or OAUTH.
        """
        if self.access_token:
            # Raw authorization.
            self._token_login()
        else:
            if self.scope and self.client_id and self.redirect_url and self.state:
                # OAUTH authorization.
                self._oauth_login()
            else:
                if any((self.scope, self.client_id, self.redirect_url, self.state)):
                    raise GitflicExceptions(
                        "Not found one of params for OAUTH, you are required to send ALL params from ('scope', 'client_id', 'redirect_url', 'state')! "
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

        # OAUTH authorization.
        raise GitflicExceptions("OAUTH not implemented yet! Use raw access_token authorization.")

        # redirect_url = urllib.parse.quote_plus(self.redirect_url)
        # webbrowser.open(OAUTH_URL.format(self.scope, self.client_id, redirect_url, self.state))
        # url = input("Paste redirect url: ")
        # r = self.session.get("").json()
        # print(r)
        # self.session.headers.update({"Authorization": "token " + "null"})
        # self.check_token()

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
