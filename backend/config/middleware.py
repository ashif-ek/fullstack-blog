import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse

from core.logging_context import clear_request_context, set_request_context


class RequestContextMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        user_id = "anonymous"
        if hasattr(request, "user") and getattr(request.user, "is_authenticated", False):
            user_id = str(getattr(request.user, "id", "anonymous"))

        set_request_context(request_id=request_id, user_id=user_id)
        request.request_id = request_id

        try:
            response = self.get_response(request)
        finally:
            clear_request_context()

        response["X-Request-ID"] = request_id
        return response
