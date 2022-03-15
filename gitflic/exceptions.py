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
    reason = "Нет прав для доступа."
    reason_ru = "There are no access rights."


class NotFound(GitflicExceptions):
    error_code = 404
    reason = "No data was found for the query."
    reason_ru = "Данные по запросу не найдены."
