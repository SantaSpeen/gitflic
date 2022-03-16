"""
All exceptions that may be raised from Gitflic API wrapper.
"""

class GitflicExceptions(Exception):
    error_code: int = 1
    reason: str = None
    reason_ru: str = None


class AuthError(GitflicExceptions):
    error_code = 403
    reason = None
    reason_ru = None


class NoRights(GitflicExceptions):
    error_code = 403
    reason = "There are no access rights."
    reason_ru = "Нет прав для доступа."


class NotFound(GitflicExceptions):
    error_code = 404
    reason = "No data was found for the query."
    reason_ru = "Данные по запросу не найдены."
