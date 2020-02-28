from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from django.urls import path

urlpatterns = [
	path('categories/', views.CategoryList.as_view()),
	path('category/<int:pk>/', views.CategoryDetail.as_view()),
	path('products/', views.ProductList.as_view()),
	path('product/<int:pk>/', views.ProductDetail.as_view()),
	path('users/', views.UserList.as_view()),
	path('users/<int:pk>/', views.UserDetail.as_view()),
	]

urlpatterns = format_suffix_patterns(urlpatterns)