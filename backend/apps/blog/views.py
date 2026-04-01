from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from .models import Post
from .serializers import PostSerializer


class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PostPagination

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views using F() expression to prevent race conditions
        Post.objects.filter(pk=instance.pk).update(views=F("views") + 1)
        # Refresh instance from db so serialized data reflects the new count
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "")
        if not query:
            # If no query, return normally paginated standard queryset
            page = self.paginate_queryset(self.get_queryset())
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        search_query = SearchQuery(query)
        queryset = (
            Post.objects.filter(search_vector=search_query)
            .annotate(rank=SearchRank(F("search_vector"), search_query))
            .order_by("-rank")
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
