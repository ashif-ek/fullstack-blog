import uuid
import logging

logger = logging.getLogger(__name__)


class RequestLogMiddleware:
    """
    Middleware to:
    - Generate a unique request_id (UUID4) per request
    - Attach it to request.request_id
    - Add it to response headers as X-Request-ID
    - Log method, path, status_code, and request_id
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate and attach request ID
        request_id = str(uuid.uuid4())
        request.request_id = request_id

        # Process the request
        response = self.get_response(request)

        # Log details
        logger.info(
            f"Method: {request.method} | Path: {request.path} | "
            f"Status: {response.status_code} | Request-ID: {request_id}"
        )

        # Add header to response
        response["X-Request-ID"] = request_id

        return response
