from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.exceptions import ValidationError
from .serializers import TripPackageSerializer
from authorization.permissions import IsPackageMaker

class PackageCreateView(APIView):
    permission_classes = [IsAuthenticated, IsPackageMaker]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        try:
            serializer = TripPackageSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    'status': 'success',
                    'message': 'Trip package created successfully',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {
                    'status': 'error',
                    'message': str(e),
                    'errors': e.message_dict if hasattr(e, 'message_dict') else {'error': str(e)}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': 'Failed to create trip package',
                    'errors': {'error': str(e)}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        