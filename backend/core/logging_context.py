import json
import logging
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

_request_id: ContextVar[str] = ContextVar("request_id", default="-")
_user_id: ContextVar[str] = ContextVar("user_id", default="-")


def set_request_context(request_id: str, user_id: str) -> None:
    _request_id.set(request_id)
    _user_id.set(user_id)


def clear_request_context() -> None:
    _request_id.set("-")
    _user_id.set("-")


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id.get()
        record.user_id = _user_id.get()
        return True


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "user_id": getattr(record, "user_id", "-"),
        }

        if record.exc_info:
            payload["error_trace"] = self.formatException(record.exc_info)

        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(payload, default=str)
