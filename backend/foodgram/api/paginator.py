from rest_framework.pagination import (
    PageNumberPagination as DjangoPageNumberPagination
)


class PageNumberPagination(DjangoPageNumberPagination):
    page_size_query_param = 'limit'
