from .models import Category,Product
from .serializers import CategorySerializer,ProductSerializer,UserSerializer
from .permissions import IsOwnerOrReadOnly , ReadOnly

from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions

from django.contrib.auth.models import User



class UserList(mixins.ListModelMixin,
				mixins.CreateModelMixin,
				generics.GenericAPIView):
	'''
	user.is_staff為True時才會允許POST權限，未身分驗證以及一般使用者只能GET。
	'''
	permission_classes = [permissions.IsAdminUser|ReadOnly] #使用 OR (|) 結合兩種不同的權限管理
	queryset = User.objects.all()
	serializer_class = UserSerializer
	
	def get(self, request, *args, **kwargs):
		return self.list(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)

class UserDetail(generics.RetrieveAPIView):
	'''
	user.is_staff為True時才會允許權限。
	'''
	permission_classes = [permissions.IsAdminUser]
	queryset = User.objects.all()
	serializer_class = UserSerializer


class CategoryList(mixins.ListModelMixin,
					mixins.CreateModelMixin,
					generics.GenericAPIView):
	'''
	只有驗證過的user可以寫入，未驗證的user只有readonly
	'''
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	
	
	def get(self, request, *args, **kwargs):
		return self.list(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)

class CategoryDetail(mixins.RetrieveModelMixin,
					mixins.UpdateModelMixin,
					mixins.DestroyModelMixin,
				generics.GenericAPIView):
	'''
	只有驗證過的user可以寫入，未驗證的user只有readonly
	'''
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	
	def get(self, request, *args, **kwargs):
		return self.retrieve(request, *args, **kwargs)

	def put(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

	def delete(self, request, *args, **kwargs):
		return self.destroy(request, *args, **kwargs)

class ProductList(mixins.ListModelMixin,
					mixins.CreateModelMixin,
					generics.GenericAPIView):
	'''
	只有驗證過的owner可以寫入，未驗證的user、有驗證但非owner只有readonly
	'''
	permission_classes = [permissions.IsAuthenticatedOrReadOnly , IsOwnerOrReadOnly]
	#queryset = Product.objects.all()
	serializer_class = ProductSerializer	
	
	def get_queryset(self):
		"""
		透過override get_queryset() 完成filter的功能
		使用可以使用查詢參數category、username對product進行filter
		example : http://192.168.1.111:8000/products/?category=book&username=edgar
		"""
		queryset = Product.objects.all()
		category = self.request.query_params.get('category' , None)
		username = self.request.query_params.get('username' , None)
		if category is not None:
			queryset = queryset.filter(category__name=category)
		if username is not None:
			queryset = queryset.filter(owner__username=username)
		return queryset
	
	def get(self, request, *args, **kwargs):
		return self.list(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)
		
	def perform_create(self, serializer):
		serializer.save(owner=self.request.user)

class ProductDetail(mixins.RetrieveModelMixin,
					mixins.UpdateModelMixin,
					mixins.DestroyModelMixin,
				generics.GenericAPIView):
	'''
	只有驗證過的owner可以寫入，未驗證的user、有驗證但非owner只有readonly
	'''
	permission_classes = [permissions.IsAuthenticatedOrReadOnly , IsOwnerOrReadOnly]
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	
	def get(self, request, *args, **kwargs):
		return self.retrieve(request, *args, **kwargs)

	def put(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

	def delete(self, request, *args, **kwargs):
		return self.destroy(request, *args, **kwargs)