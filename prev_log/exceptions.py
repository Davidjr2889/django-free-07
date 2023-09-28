import json

from django.http import HttpResponse, HttpResponseBadRequest


class BasePrevLogException(Exception):
    """Exception class for prev log errors"""

    error: str
    details: str
    status: int

    def __init__(
        self,
        error="prev_log.error",
        details="prev_log.error.details",
        status=500,
        *args: object
    ) -> None:
        self.error = error
        self.details = details
        self.status = status

        super().__init__(*args)

    def error_response(self):
        return json.dumps(
            {
                "error": self.error,
                "details": self.details,
            }
        )

    def http_return(self):
        return HttpResponse(
            status=self.status,
            content=self.error_response(),
        )


class PrevLogBadRequestException(BasePrevLogException):
    def __init__(self, error, details, *args: object) -> None:
        super().__init__(error, details, 400, *args)

    def http_return(self):
        return HttpResponseBadRequest(
            content=self.error_response(),
        )
