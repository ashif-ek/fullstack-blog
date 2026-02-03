from rest_framework.response import Response
from rest_framework import status


def api_response(
    success: bool, data=None, error: str = None, status_code=status.HTTP_200_OK
):
    """
    Returns a standardized Response object.

    Structure:
    {
        "success": boolean,
        "data": any,
        "error": string | null
    }
    """
    payload = {"success": success, "data": data, "error": error}
    return Response(payload, status=status_code)
