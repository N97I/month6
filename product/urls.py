from django.urls import path
from .views import (
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
    ProductListCreateAPIView,
    ProductDetailAPIView,
    ReviewViewSet,
    ProductWithReviewsAPIView,
    OwnerProductListAPIView
)

urlpatterns = [
    path('', ProductListCreateAPIView.as_view()),
    path('<int:id>/', ProductDetailAPIView.as_view()),
    path('categories/', CategoryListCreateAPIView.as_view()),
    path('categories/<int:id>/', CategoryDetailAPIView.as_view()),
    path('reviews/', ProductWithReviewsAPIView.as_view()),
    path('reviews/<int:id>/', ReviewViewSet.as_view({
        'get': 'list',
        'post': 'create'})),
    path('reviews/<int:id>/', ReviewViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    path('my/', OwnerProductListAPIView.as_view()),
]