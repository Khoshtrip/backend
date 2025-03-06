import uuid
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from utils.cache_decorators import cache_view
from utils.cache_monitoring import monitored_cache_view, MonitoredCacheMixin
from .models import TripPackage, Transaction, PurchaseHistory, PackageRating
from .serializers import TripPackageSerializer, TripPackageListSerializer, PurchasePackageSerializer
from authorization.permissions import IsPackageMaker, IsPackageMakerOrCustomer
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.conf import settings
from utils.cache_utils import invalidate_model_caches
from rest_framework.decorators import api_view

class PackagePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'per_page'
    max_page_size = 100

class PackageListView(MonitoredCacheMixin, APIView):
    permission_classes = [IsAuthenticated, IsPackageMakerOrCustomer]
    pagination_class = PackagePagination
    cache_timeout = 60 * 5  # 5 minutes
    cache_key_prefix = 'package_list'

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

class PackageDetailView(MonitoredCacheMixin, APIView):
    permission_classes = [IsAuthenticated, IsPackageMakerOrCustomer]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    cache_timeout = 60 * 5  # 5 minutes
    cache_key_prefix = 'package_detail'

    def get(self, request, package_id):
        try:
            package = TripPackage.objects.get(id=package_id)
            serializer = TripPackageSerializer(package)
            return Response({
                'status': 'success',
                'message': 'Package details retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except TripPackage.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Package not found',
            }, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, package_id):
        if not IsPackageMaker().has_permission(request, self):
            return Response(
                {
                    'status': 'error',
                    'message': 'Only package makers can edit packages'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        package = get_object_or_404(TripPackage, id=package_id)

        try:
            serializer = TripPackageSerializer(package, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {
                    'status': 'success',
                    'message': 'Trip package updated successfully',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
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
                    'message': 'Failed to update trip package',
                    'errors': {'error': str(e)}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, package_id):
        if not IsPackageMaker().has_permission(request, self):
            return Response(
                {
                    'status': 'error',
                    'message': 'Only package makers can delete packages'
                },
                status=status.HTTP_403_FORBIDDEN
            )
            
        package = get_object_or_404(TripPackage, id=package_id)
        package.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GenerateTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, package_id):
        package = get_object_or_404(TripPackage, id=package_id)

        # Get the quantity from the request data
        quantity = request.data.get('quantity', 1)

        # Validate available units
        if package.available_units < quantity:
            return Response(
                {
                    'status': 'error',
                    'message': f'Not enough available units for this package. Available: {package.available_units}, Requested: {quantity}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate a unique transaction ID
        transaction_id = str(uuid.uuid4())

        # Create a pending transaction
        transaction = Transaction.objects.create(
            transaction_id=transaction_id,
            user=request.user,  # Use the authenticated user
            package=package,
            status='pending',
            quantity=quantity
        )

        return Response(
            {
                'status': 'success',
                'message': 'Transaction ID generated successfully',
                'data': {
                    'transaction_id': transaction_id,
                    'package_id': package.id,
                    'created_at': transaction.created_at,
                    'quantity': quantity
                }
            },
            status=status.HTTP_201_CREATED
        )

class PurchasePackageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, transaction_id):
        # Find the transaction
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)

        # Check if the transaction is already completed or cancelled
        if transaction.status != 'pending':
            return Response(
                {
                    'status': 'error',
                    'message': 'Transaction is already completed or cancelled'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate request data
        serializer = PurchasePackageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'status': 'error',
                    'message': 'Invalid payment details',
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        card_number = serializer.validated_data['card_number']

        # Mark the transaction as completed
        transaction.status = 'completed'
        transaction.purchase_date = timezone.now()
        transaction.card_number = card_number[-4:]  # Store only the last 4 digits
        transaction.save()

        # Update available units
        package = transaction.package
        package.available_units -= transaction.quantity
        package.save()

        # Save purchase history
        total_price = package.price * transaction.quantity
        PurchaseHistory.objects.create(
            user=request.user,
            package=package,
            transaction=transaction,
            purchase_date=transaction.purchase_date,
            quantity=transaction.quantity,
            total_price=total_price
        )

        return Response(
            {
                'status': 'success',
                'message': 'Package purchased successfully',
                'data': {
                    'package_id': package.id,
                    'user_id': request.user.id,
                    'transaction_id': transaction.transaction_id,
                    'purchase_date': transaction.purchase_date,
                    'quantity': transaction.quantity,
                    'total_price': total_price
                }
            },
            status=status.HTTP_200_OK
        )

class CancelTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, transaction_id):
        # Find the transaction
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)

        # Check if the transaction is already completed or cancelled
        if transaction.status != 'pending':
            return Response(
                {
                    'status': 'error',
                    'message': 'Transaction is already completed or cancelled'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark the transaction as cancelled
        transaction.status = 'cancelled'
        transaction.save()

        return Response(
            {
                'status': 'success',
                'message': 'Transaction cancelled successfully',
                'data': {
                    'transaction_id': transaction.transaction_id,
                    'status': transaction.status
                }
            },
            status=status.HTTP_200_OK
        )

class UserPurchaseHistoryView(MonitoredCacheMixin, APIView):
    permission_classes = [IsAuthenticated]
    cache_timeout = 60 * 5  # 5 minutes
    cache_key_prefix = 'user_purchase_history'

    def get(self, request):
        # Retrieve the purchase history for the authenticated user
        purchase_history = PurchaseHistory.objects.filter(user=request.user).select_related('package', 'transaction')

        # Serialize the data
        history_data = []
        for purchase in purchase_history:
            history_data.append({
                'package_name': purchase.package.name,
                'purchase_date': purchase.purchase_date,
                'quantity': purchase.quantity,
                'total_price': purchase.total_price,
                'transaction_id': purchase.transaction.transaction_id
            })

        return Response(
            {
                'status': 'success',
                'data': history_data
            },
            status=status.HTTP_200_OK
        )
class RatePackageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, package_id, format=None):
        try:
            package = TripPackage.objects.get(id=package_id)
        except TripPackage.DoesNotExist:
            return Response({"error": "Package not found."}, status=status.HTTP_404_NOT_FOUND)

        rating = request.data.get('rating')
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            return Response({"error": "Rating must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if rating < 1 or rating > 5:
            return Response({"error": "Rating must be between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        # Attempt to get an existing rating for this user and package.
        rating_obj, created = PackageRating.objects.get_or_create(
            user=user,
            package=package,
            defaults={'rating': rating}
        )
        if not created:
            # If the rating exists, update it.
            rating_obj.rating = rating
            rating_obj.save()

        # Update the package's aggregate rating.
        package.update_rating(rating)

        return Response({
            "message": "Rating submitted successfully.",
            "package_rating": package.rating,
            "ratings_count": package.ratings_count,
        }, status=status.HTTP_200_OK)


class GetPackageRatingAPIView(APIView):
    permission_classes = [] 

    def get(self, request, package_id, format=None):
        try:
            package = TripPackage.objects.get(id=package_id)
        except TripPackage.DoesNotExist:
            return Response({"error": "Package not found."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "package_id": package.id,
            "rating": package.rating,
            "ratings_count": package.ratings_count,
        }
        return Response(data, status=status.HTTP_200_OK)
