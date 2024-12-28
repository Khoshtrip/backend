from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

class CustomPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 50

    def get_paginated_response(self, data):
        return Response({
            'total': self.count,
            'offset': self.offset,
            'limit': self.limit,
            'products': data
        }) 