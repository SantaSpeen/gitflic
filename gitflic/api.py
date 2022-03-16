"""
Main Gitflic API wrapper.
"""

from enum import Enum

from .auth import GitflicAuth
from .exceptions import (
    NotFound, NoRights, GitflicExceptions
)


API_URL = 'https://api.gitflic.ru'


class GitflicAPIMethods(Enum):
    """ Methods that you may use for calling API. """
    USER_ME = "/user/me"
    USER = "/user"
    # There is not all methods, please expand if you need some other method.


class Gitflic:
    """
    Gitflic API wrapper.
    """

    def __init__(self, gf_session: GitflicAuth):
        """
        :param gf_session: Authorized session from GitflicAuth.
        """
        self.session = gf_session.session

    @staticmethod
    def _response_handler(response):
        """ 
        Handles HTTP response from Gitflic API. 
        :param response: HTTP response.
        :return: Exception or valid JSON.
        """
        code = response.status_code

        if code == 200:
            return response.json()

        url = response.url
        if code == 403:
            raise NoRights(f"Access denied for '{url}'")
        elif code == 404:
            raise NotFound(f"Location '{url}' not found")

        raise GitflicExceptions(f"Gitflic sent unknown error with HTTP code: {code}. Response: {response.text}")

    def call(self, method: str, *args, **kwargs):
        """
        Calls API method on server side.
        :param method: API method of Gitflic to call.
        :return: Exception or valid JSON.
        """
        response = self.session.get(API_URL + method, *args, **kwargs)
        return self._response_handler(response)

    def reg_call(self, method: str):

        l = lambda add_to_method="", *_args, **_kwargs: self.call(method+add_to_method, *_args, **_kwargs)
        l.__name__ = method.replace("/", "_")

        return l
