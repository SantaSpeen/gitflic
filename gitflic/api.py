"""
Main Gitflic API wrapper.
"""
from .auth import GitflicAuth
from .exceptions import (
    NotFound, AccessDenied, GitflicExceptions
)


API_URL = 'https://api.gitflic.ru'


def _fix_none(obj):
    if isinstance(obj, tuple) or isinstance(obj, list):
        obj = list(obj)
        for index, item in enumerate(obj):
            if item is None:
                obj[index] = ''

    elif isinstance(obj, dict):
        for k, v in obj.items():
            if v is None:
                obj[k] = ''

    return obj


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
            raise AccessDenied(f"Access denied for '{url}'")
        elif code == 404:
            raise NotFound(f"Location '{url}' not found")

        raise GitflicExceptions(f"Gitflic sent unknown error with HTTP code: {code}. Url: {url}. Response: {response.text}")

    def call(self, method: str, *args, **kwargs):
        """
        Calls API method on server side.
        :param method: API method of Gitflic to call.
        :return: Exception or valid JSON.
        """
        response = self.session.get(API_URL + method, *args, **kwargs)
        return self._response_handler(response)

    def __reg_call_handler(self, *args, end=None, **kwargs):
        if end is None:
            end = ""
        args: list = _fix_none(args)
        kwargs: dict = _fix_none(kwargs)
        disable_formatting: bool = kwargs.pop("disable_formatting", False)
        method: str = kwargs['__gitflic_method_name__']

        # If not need formatting
        if not disable_formatting:
            if len(args) > 0:
                try:
                    if "%" in method:
                        method %= tuple(args)
                    else:
                        method = method.format(*args)

                except Exception as e:
                    raise GitflicExceptions(f"Formatting error: {e!r}; In call: '{method}; Args: {args}'")
            elif len(kwargs) > 0:
                if "%" in method:
                    method %= kwargs
                else:
                    method = method.format_map(kwargs)

        method += end

        return self.call(method)

    def reg_call(self, method_string: str):

        func = lambda *args, **kwargs: self.__reg_call_handler(*args, **kwargs, __gitflic_method_name__=method_string)
        func.__name__ = method_string

        return func
