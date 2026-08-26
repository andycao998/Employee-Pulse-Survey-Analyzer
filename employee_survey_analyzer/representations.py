class SurveyError(Exception):
    """ Base exception for all errors here """
    def __init__(self, code: str, status: int, detail: str | None = None) -> None:
        super().__init__(detail or code)
        self.code = code
        self.status = status
        self.detail = detail

class SurveyNotFoundError(SurveyError):
    """ Represents that the survey was not found """

class SurveyInvalidDateRangeError(SurveyError):
    """ Represents that the survey close date is before the open date """

class SurveyUnavailableError(SurveyError):
    """ Represents that the survey is either closed or not yet open """

class SurveyUnmodifiableError(SurveyError):
    """ Represents that the survey has a response and can no longer be updated """
    