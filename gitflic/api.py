from .auth import GitflicAuth
from .exceptions import NotFound, NoRights, GitflicExceptions

API_URL = 'https://api.gitflic.ru'


class Gitflic:

    def __init__(self, gf_session: GitflicAuth):
        """

        :param gf_session:
        """
        self.session = gf_session.session

    @staticmethod
    def _response_handler(response):
        code = response.status_code
        if code == 200:
            return response.json()
        url = response.url
        if code == 403:
            raise NoRights(f"No rights for '{url}'")
        elif code == 404:
            raise NotFound(f"Response '{url}' not found")

        raise GitflicExceptions(f"Gitflic send error: {code}. {response.text}")

    def call(self, method, *args, **kwargs):
        """

        :param method:
        :param args:
        :param kwargs:
        :return:
        """
        response = self.session.get(API_URL + method, *args, **kwargs)
        return self._response_handler(response)

    def reg_call(self, method: str):

        l = lambda add_to_method="", *_args, **_kwargs: self.call(method+add_to_method, *_args, **_kwargs)
        l.__name__ = method.replace("/", "_")

        return l
