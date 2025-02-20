from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from .models import TripPackage
from .serializers import TripPackageSerializer, TripPackageListSerializer
from authorization.permissions import IsPackageMaker, IsPackageMakerOrCustomer
from datetime import datetime
from django.shortcuts import get_object_or_404

class PackagePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'per_page'
    max_page_size = 100

class PackageListView(APIView):
    permission_classes = [IsAuthenticated, IsPackageMakerOrCustomer]
    pagination_class = PackagePagination

    def get(self, request):
        total_packages = TripPackage.objects.all().count()

        # Get query parameters
        search = request.query_params.get('search')
        price_min = request.query_params.get('price_min')
        price_max = request.query_params.get('price_max')
        sort_by = request.query_params.get('sort_by')
        published = request.query_params.get('published')
        date_start = request.query_params.get('date_start')
        date_end = request.query_params.get('date_end')
        hotel_name = request.query_params.get('hotel_name')
        flight_airline = request.query_params.get('flight_airline')

        queryset = TripPackage.objects.select_related('flight', 'hotel').prefetch_related('activities')

        if search:
            queryset = queryset.filter(name__icontains=search)

        if price_min:
            try:
                price_min = float(price_min)
                queryset = queryset.filter(price__gte=price_min)
            except ValueError:
                return Response(
                    {'error': 'Invalid price_min value'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if price_max:
            try:
                price_max = float(price_max)
                queryset = queryset.filter(price__lte=price_max)
            except ValueError:
                return Response(
                    {'error': 'Invalid price_max value'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if date_start:
            try:
                date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
                queryset = queryset.filter(start_date__gte=date_start)
            except ValueError:
                return Response(
                    {'error': 'Invalid date_start format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if date_end:
            try:
                date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
                queryset = queryset.filter(end_date__lte=date_end)
            except ValueError:
                return Response(
                    {'error': 'Invalid date_end format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if hotel_name:
            queryset = queryset.filter(hotel__name__icontains=hotel_name)

        if flight_airline:
            queryset = queryset.filter(flight__name__icontains=flight_airline)

        if published is not None:
            published = published.lower() == 'true'
            queryset = queryset.filter(published=published)

        if sort_by:
            if sort_by == 'price':
                queryset = queryset.order_by('price')
            elif sort_by == 'date':
                queryset = queryset.order_by('start_date')

        # Apply pagination
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        if not paginated_queryset:
            return Response(
                {
                    'status': 'success',
                    'message': 'No packages found',
                    'data': {
                        'total': 0,
                        'page': 1,
                        'per_page': paginator.page_size,
                        'packages': []
                    }
                },
                status=status.HTTP_200_OK
            )

        # Serialize the data
        serializer = TripPackageListSerializer(paginated_queryset, many=True)

        return Response(
            {
                'status': 'success',
                'data': {
                    'total': paginator.page.paginator.count,
                    'page': paginator.page.number,
                    'per_page': paginator.page_size,
                    'packages': serializer.data
                }
            },
            status=status.HTTP_200_OK
        )

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

class PackageDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPackageMaker]

    def delete(self, request, package_id):
        package = get_object_or_404(TripPackage, id=package_id)
        
        package.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
        