from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from django.urls import path

urlpatterns = [
	path('apis/categories/', views.CategoryList.as_view()),
	path('apis/category/<int:pk>/', views.CategoryDetail.as_view()),
	path('apis/products/', views.ProductList.as_view()),
	path('apis/product/<int:pk>/', views.ProductDetail.as_view()),
	path('apis/users/', views.UserList.as_view()),
	path('apis/user/<int:pk>/', views.UserDetail.as_view()),
	]

#urlpatterns = format_suffix_patterns(urlpatterns)