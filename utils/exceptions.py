from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.response import Response
from .error_codes import ErrorCodes

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    error_response = {
        'status': 'error',
        'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
        'code': getattr(exc, 'code', 'INTERNAL_ERROR'),
        'errors': None
    }
    
    if response is not None:
        if isinstance(response.data, dict):
            error_response['errors'] = response.data
        response.data = error_response
    else:
        response = Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response

class AuthenticationError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = ErrorCodes.INVALID_CREDENTIALS

class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = ErrorCodes.INVALID_INPUT

class ResourceNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = ErrorCodes.NOT_FOUND

class PermissionError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = ErrorCodes.PERMISSION_DENIED