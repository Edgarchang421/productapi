# productapi  
透過django、djangorestframework建立簡易的產品資料API  

## Packages
pip install django==2.2.12 djangorestframework djangorestframework-simplejwt  
pip install -U drf-yasg  

使用 django 作為整體框架  
使用 djangorestframework 提供建立 API 時會需要的各種工具  
透過 djangorestframework-simplejwt 使用 json web token 驗證機制  
drf-yasg 可以迅速建立 API 文件  官方文件中建議在安裝時使用 -U : --upgrade 會更新所有相關套件到最新版本  

## models  
```
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
	name = models.CharField(max_length=50);

	def __str__(self):
		return self.name

class Product(models.Model):
	category = models.ForeignKey(Category , on_delete = models.CASCADE)
	name = models.CharField(max_length = 50)
	description = models.TextField(default = '尚未有產品說明')
	image = models.ImageField(upload_to = 'media' , blank = True)
	stock = models.PositiveIntegerField(default = 0) 
	price = models.PositiveIntegerField(default = 0) 
	owner = models.ForeignKey(User , on_delete=models.CASCADE , related_name='products')

	def __str__(self):
		return self.name
```
Category儲存產品類別的名稱，Product儲存單一產品的詳細資料  
Product的category field使用ForeignKey與Category建立關聯  
  
如果是使用default FileSystemStorage，則ImageField會將圖片儲存在settings.py中的MEDIA_ROOT  
django官方網站說明 :   
https://docs.djangoproject.com/en/3.0/ref/models/fields/#django.db.models.FileField.upload_to  
  
如果已經要上傳的檔案在該資料夾中已經有相同的file name，FileSystemStorage會修改檔案名稱，取得一個unique name  
因此不用擔心檔案名稱的儲存問題  
參考自官方文件 :   
https://docs.djangoproject.com/en/3.0/ref/files/storage/#django.core.files.storage.Storage.save  
  
## serializers  
```
from .models import Category,Product
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
	products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())
	class Meta:
		model = User
		fields = ['id', 'username', 'is_staff' , 'products']

class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = ['id' , 'name']


class ProductSerializer(serializers.ModelSerializer):
	owner = serializers.ReadOnlyField(source='owner.username')
	class Meta:
		model = Product
		fields = ['id' , 'category' , 'name' , 'description' , 'image' , 'stock' , 'price' , 'owner']
```
使用djangorestframework提供的serializers.ModelSerializer  
建立與model相對應的serializer  

如果考量到效能問題，也可以只使用REST framework的serializers.Serializer  

## views  
只列出ProductList和Productdetail  
```
class ProductList(mixins.ListModelMixin,
					mixins.CreateModelMixin,
					generics.GenericAPIView):
	'''
	只有驗證過的owner可以寫入，未驗證的user、有驗證但非owner只有readonly
	'''
	permission_classes = [permissions.IsAuthenticatedOrReadOnly]
	#queryset = Product.objects.all()
	serializer_class = ProductSerializer	
	
	def get_queryset(self):
		"""
		透過override get_queryset() 完成filter的功能
		使用可以使用查詢參數category、username對product進行filter
		example : /products/?category=book&username=edgar
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
```
兩個class繼承了generics.GenericAPIView以及使用mixins提供不同的HTTP method  

兩個class分別使用了不同的permission_classes  
權限控制為REST framework提供的permissions.IsAuthenticatedOrReadOnly，以及自己建立的IsOwnerOrReadOnly  
IsAuthenticatedOrReadOnly可以使得已經驗證的USER才可以在PorductList讀取以及新增資料，未驗證的user只有readonly權限  
  
ProductDetail多使用了IsOwnerOrReadOnly，已驗證的user可以讀取但不能寫入，只有經過驗證的data owner可以讀取以及寫入  
  
在ProducyLIst透過override get_queryset()提供filter的功能，可以使用username和category作為參數，列出客戶端需求的資料  

## permissions  
```
from rest_framework.permissions import BasePermission , SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
	def has_object_permission(self, request, view, obj):
		# Read permissions are allowed to any request,
		# so we'll always allow GET, HEAD or OPTIONS requests.
		if request.method in SAFE_METHODS:
			return True

		# Write permissions are only allowed to the owner of the product.
		return obj.owner == request.user
		
class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
```
IsOwnerOrReadOnly、ReadOnly這兩個permission class是REST framework沒有提供的  
因此要透過繼承rest_framework.permissions的BasePermission  
然後override其中的method達成自己的需求  
  
Custom permission參考自官方文件  
https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions  

## apiapp/urls  
```
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
```
因為是使用class-based views所以要使用 .as_view()完成urlpattern  

urlpatterns = format_suffix_patterns(urlpatterns)  
可以使得endpoint可以處理 http://example.com/api/items/4.json 之類加上格式的URL  
但因為會使得drf-yasg的Validation無法通過，故先註解掉  
https://drf-yasg.readthedocs.io/en/stable/readme.html#using-swagger-cli  
  
## tests  
主要有:  
class CategoriesListTest(TestCase): #測試CategoryList的GET和POST，分為匿名user和已驗證過的user。  
class CategoryDetailTest(TestCase):  #測試CategoryDetail的GET、PUT和DELET，分為匿名user和已驗證過的user。  
class ProductListTest(TestCase):  #測試ProductList的GET、POST，分為匿名user和已驗證過的user。  
class ProductDetailTest(TestCase): #測試ProductDetail的GET、PUT和DELET，分為匿名user、已驗證過的user、已驗證的user但非owner。  

對於四個客戶端可以讀寫的API endpoint進行介面測試  
  
因為使用了djangorestframework-simplejwt套件，建立了json web token的驗證機制  
所以在test中寫了get_JSON_Web_Token()以便需要驗證的endpoint進行驗證  
```
def get_JSON_Web_Token(self):
		##由於POST method需要使用JWT驗證，故建立此method，方便重複使用
		obtaintJsonWebToken = self.client.post('/api/token/' , 
			{'username':'jacob' , 'password':'top1secret23'} , 
			content_type='application/json'
			)
		JWT = obtaintJsonWebToken.data
		
		return JWT
```

## settings
```
'apiapp',
'rest_framework',
'drf_yasg',
```
INSTALLED_APPS list中除了需要加入自己建立app，還需要加上rest_framework以及用來製作API文件的drf_yasg  

```
REST_FRAMEWORK = {
	#設定驗證方法，若沒有設定DEFAULT_AUTHENTICATION_CLASSES，會將request.user設定為instance of django.contrib.auth.models.AnonymousUser
	'DEFAULT_AUTHENTICATION_CLASSES': (
		'rest_framework_simplejwt.authentication.JWTAuthentication',
	),
	#設定test時，發出request的format
	'TEST_REQUEST_DEFAULT_FORMAT': 'json'
	}
```
REST framework用來設定djangorestframework的各種機制，驗證、權限、分頁、流量限制...等等API設定  
官方網站說明 :   
https://www.django-rest-framework.org/api-guide/settings/  

```
STATIC_URL = '/static/' #可通過http://127.0.0.1/static/***/訪問

MEDIA_ROOT = '/home/edgar/productapi/media/'  #客戶端上傳的圖片存放資料夾 : /media/

MEDIA_URL = '/media/'  #可通過http://127.0.0.1/media/***/訪問
```
因為有使用imagefield，因此需要設定存放的資料夾以及URL  
官方網站說明 :   
https://docs.djangoproject.com/en/3.0/howto/static-files/  

## URLconf
提供client獲取json web token的endpoint所使用的view   
```
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
```
  
提供client獲取json web token的endpoint  
```
	path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
```
  
製作API文件需要取得view的結構   
```
schema_view = get_schema_view(
   openapi.Info(
      title="Product API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="ken2798315601@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
```
  
使用正規表達式的re_path製作API文件的endpoint   
```
re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
```
  
讓user可以直接在瀏覽器查看static file   
```
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
  
REST framework所提供的basi auth登入頁面   
```
urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
```
