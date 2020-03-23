from django.test import TestCase , Client
from django.contrib.auth.models import AnonymousUser, User
from django.core.files import File

from .views import CategoryList
from .models import Category , Product

from io import BytesIO

class CategoriesListTest(TestCase): #測試CategoryList的GET和POST，分為匿名user和已驗證過的user。
	##建立categoet的資料，方便AssertEqual時重複使用
	category_list_data = [
				{
					'id': 1, 
					'name': 'book'
				},
				{
					'id': 2, 
					'name': 'guitar'
				}
			]
	
	def setUp(self):
		#建立test database，然後新增一個普通user、兩個category的instance
		self.regularuser = User.objects.create_user(username='jacob',  password='top1secret23')
		
		Category.objects.create(name = 'book')
		Category.objects.create(name = 'guitar')

	def get_JSON_Web_Token(self):
		##由於POST method需要使用JWT驗證，故建立此method，方便重複使用
		obtaintJsonWebToken = self.client.post('/api/token/' , 
			{'username':'jacob' , 'password':'top1secret23'} , 
			content_type='application/json'
			)
		JWT = obtaintJsonWebToken.data
		
		return JWT

	def test_AnonymousUser_get(self): #測試未驗證的user使用get method
		response = self.client.get('/apis/categories/')
		
		self.assertEqual(response.status_code , 200)
		self.assertEqual(response.data , self.category_list_data)
		
	def test_AuthenticatedUser_get(self): #測試已驗證的user使用get method
		JWT = self.get_JSON_Web_Token()
		
		##建立有Authorization: Bearer + access token的header的Client() instance
		c = Client(HTTP_AUTHORIZATION='Bearer ' + JWT['access'])
		response = c.get('/apis/categories/')
		
		self.assertEqual(response.status_code , 200)
		self.assertEqual(response.data, self.category_list_data)
	
	def test_AnonymousUser_post(self): #測試未驗證的user使用post method
		response = self.client.post('/apis/categories/' , {'name':'CD'})
		
		self.assertEqual(response.status_code , 401)
		
	def test_AuthenticatedUser_post(self): #測試已驗證的user使用post method
		JWT = self.get_JSON_Web_Token()
		
		##建立有Authorization: Bearer + access token的header的Client() instance，完成post method
		c = Client(HTTP_AUTHORIZATION='Bearer ' + JWT['access'])
		response = c.post('/apis/categories/' , {'name':'CD'})
		
		self.assertEqual(response.status_code , 201)
		self.assertEqual(response.data , {'id': 3 , 'name':'CD'} )
		
class CategoryDetailTest(TestCase):  #測試CategoryDetail的GET、PUT和DELET，分為匿名user和已驗證過的user。
	
	def setUp(self):
		#建立test database，然後新增一個普通user、一個category的instance
		self.user = User.objects.create_user(username='jacob',  password='top1secret23')
		
		Category.objects.create(name = 'book')
	
	def get_JSON_Web_Token(self):
		##由於POST、PUT、DELETE method需要使用JWT驗證，故建立此method，方便重複使用
		obtaintJsonWebToken = self.client.post('/api/token/' , 
			{'username':'jacob' , 'password':'top1secret23'} , 
			content_type='application/json'
			)
		JWT = obtaintJsonWebToken.data
		
		return JWT
	
	def test_AnonymousUser_get(self): #測試未驗證的user使用get method
		response = self.client.get('/apis/category/1/')
		
		self.assertEqual(response.status_code , 200)
		self.assertEqual(response.data , {'id': 1, 'name': 'book'} )
		
	def test_AnonymousUser_put(self): #測試未驗證的user使用put method
		response = self.client.put('/apis/category/1/' , {'name':'monitor'})
		
		self.assertEqual(response.status_code , 401)
		
	def test_AnonymousUser_delete(self): #測試未驗證的user使用delete method
		response = self.client.delete('/apis/category/1/')
		
		self.assertEqual(response.status_code , 401)
		
	def test_AuthenticatedUser_get(self): #測試已驗證的user使用get method
		JWT = self.get_JSON_Web_Token()
		
		##建立有Authorization: Bearer + access token的header的Client() instance，完成post method
		c = Client(HTTP_AUTHORIZATION='Bearer ' + JWT['access'])
		response = c.get('/apis/category/1/')
		
		self.assertEqual(response.status_code , 200)
		self.assertEqual(response.data , {'id': 1, 'name': 'book'} )
		
	def test_AuthenticatedUser_put(self): #測試已驗證的user使用put method
		JWT = self.get_JSON_Web_Token()
		
		##建立有Authorization: Bearer + access token的header的Client() instance，完成post method
		c = Client(HTTP_AUTHORIZATION='Bearer ' + JWT['access'])
		response = c.put('/apis/category/1/' , {'name':'monitor'} , content_type='application/json')
		
		self.assertEqual(response.status_code , 200)
		self.assertEqual(response.data , {'id': 1, 'name': 'monitor'} )
		
	def test_AuthenticatedUser_delete(self): #測試已驗證的user使用delete method
		JWT = self.get_JSON_Web_Token()
		
		##建立有Authorization: Bearer + access token的header的Client() instance，完成post method
		c = Client(HTTP_AUTHORIZATION='Bearer ' + JWT['access'])
		response = c.delete('/apis/category/1/')
		
		self.assertEqual(response.status_code , 204)
		self.assertEqual(response.data , None )
		
class ProductListTest(TestCase):  #測試ProductList的GET、POST，分為匿名user和已驗證過的user。
	def setUp(self):
		#建立test database，然後新增一個普通user、一個Category的instance、兩個Product的instance
		self.user = User.objects.create_user(username='jacob',  password='top1secret23')
		
		Category.objects.create(name = 'book')
		Category.objects.create(name = 'guitar')
		
		bookcategory = Category.objects.get(name = 'book')
		productowner = User.objects.get(username = 'jacob')
		
		Product.objects.create(category = bookcategory ,
			name = '科班出身的MVC網頁開發：使用Python+Django' , 
			description = '書中內容來自於團隊實際專案開發經驗和相關知識按系統撰寫而成。',
			#image = '/home/edgar/productapi/media/media/2013120517752b.jpg', 
			stock = 10 , 
			price = 550 , 
			owner = productowner
			)
		
		Product.objects.create(category = bookcategory ,
			name = 'Python Web介面開發與自動化測試' , 
			description = '本書從Web介面開發講起，理解介面是如何開發後，再學習介面測試自然就變得非常簡單。',
			#image = '/home/edgar/productapi/media/media/1.jpg' , 
			stock = 5 , 
			price = 450 , 
			owner = productowner
			)	
	
	def get_JSON_Web_Token(self):
		##由於POST method需要使用JWT驗證，故建立此method，方便重複使用
		obtaintJsonWebToken = self.client.post('/api/token/' , 
			{'username':'jacob' , 'password':'top1secret23'} , 
			content_type='application/json'
			)
		JWT = obtaintJsonWebToken.data
		
		return JWT
	
	def test_AnonymousUser_get(self): #測試未驗證的user使用get method
		response = self.client.get('/apis/products/')
		
		self.assertEqual(response.status_code , 200)
		self.assertEqual(response.data , 
			[
				{
					'id': 1,
					'category': 1,
					'name': '科班出身的MVC網頁開發：使用Python+Django',
					'description': '書中內容來自於團隊實際專案開發經驗和相關知識按系統撰寫而成。',
					'image': None ,
					'stock': 10,
					'price': 550,
					'owner': 'jacob'
				},
				{
					'id': 2,
					'category': 1,
					'name' : 'Python Web介面開發與自動化測試' , 
					'description' : '本書從Web介面開發講起，理解介面是如何開發後，再學習介面測試自然就變得非常簡單。',
					'image': None ,
					'stock': 5,
					'price': 450,
					'owner': 'jacob'
				}
			]
		)
		
	def test_AuthenticatedUser_get(self): #測試已驗證的user使用get method
		JWT = self.get_JSON_Web_Token()
		
		##建立有Authorization: Bearer + access token的header的Client() instance，完成post method
		c = Client(HTTP_AUTHORIZATION='Bearer ' + JWT['access'])
		response = c.get('/apis/products/')
		
		self.assertEqual(response.status_code , 200)
		self.assertEqual(response.data , 
			[
				{
					'id': 1,
					'category': 1,
					'name': '科班出身的MVC網頁開發：使用Python+Django',
					'description': '書中內容來自於團隊實際專案開發經驗和相關知識按系統撰寫而成。',
					'image': None ,
					'stock': 10,
					'price': 550,
					'owner': 'jacob'
				},
				{
					'id': 2,
					'category': 1,
					'name' : 'Python Web介面開發與自動化測試' , 
					'description' : '本書從Web介面開發講起，理解介面是如何開發後，再學習介面測試自然就變得非常簡單。',
					'image': None ,
					'stock': 5,
					'price': 450,
					'owner': 'jacob'
				}
			]
		)
	
	def test_AnonymousUser_post(self): #測試未驗證的user使用post method
		response = self.client.post('/apis/products/' , 
			{
				'category' : 2,
				'name' : 'Strandberg Boden Original 6',
				'description' : '方便攜帶的無頭琴',
				'image' : '/home/edgar/productapi/media/media/15.jpg',
				'stock' : 2 ,
				'price' : 72800				
			}
		)
		
		self.assertEqual(response.status_code , 401)
		
	def test_AuthenticatedUser_post(self): #測試已驗證的user使用post method
		JWT = self.get_JSON_Web_Token()
		
		##建立有Authorization: Bearer + access token的header的Client() instance，完成post method
		c = Client(HTTP_AUTHORIZATION='Bearer ' + JWT['access'])
		
		response = c.post('/apis/products/' , 
			{
				'category' : 2,
				'name' : 'Strandberg Boden Original 6',
				'description' : '方便攜帶的無頭琴',
				#'image' : '/home/edgar/productapi/media/media/15.jpg',
				'stock' : 2 ,
				'price' : 72800				
			}
		)
		
		self.assertEqual(response.status_code , 201)
		self.assertEqual(response.data , 
			{
				'id': 3,
				'category': 2,
				'name': 'Strandberg Boden Original 6',
				'description': '方便攜帶的無頭琴',
				'image': None ,
				'stock': 2,
				'price': 72800,
				'owner': 'jacob'
			}
		)

class ProductDetailTest(TestCase): #測試ProductDetail的GET、PUT和DELET，分為匿名user和已驗證過的user。
	def setUp(self):
		#建立test database，然後新增一個普通user、一個Category的instance、兩個Product的instance
		self.user = User.objects.create_user(username='jacob',  password='top1secret23')
		
		Category.objects.create(name = 'book')
		Category.objects.create(name = 'guitar')
		
		bookcategory = Category.objects.get(name = 'book')
		productowner = User.objects.get(username = 'jacob')
		
		Product.objects.create(
			category = bookcategory ,
			name = '科班出身的MVC網頁開發：使用Python+Django' , 
			description = '書中內容來自於團隊實際專案開發經驗和相關知識按系統撰寫而成。',
			#image = '/home/edgar/productapi/media/media/2013120517752b.jpg', 
			stock = 10 , 
			price = 550 , 
			owner = productowner
			)
	
	def get_JSON_Web_Token(self):
		##由於POST、PUT、DELETE method需要使用JWT驗證，故建立此method，方便重複使用
		obtaintJsonWebToken = self.client.post('/api/token/' , 
			{'username':'jacob' , 'password':'top1secret23'} , 
			content_type='application/json'
			)
		JWT = obtaintJsonWebToken.data
		
		return JWT
		
	def test_AnonymousUser_get(self): #測試未驗證的user使用get method
		response = self.client.get('/apis/product/1/')
		
		self.assertEqual(response.status_code , 200)
		self.assertEqual(response.data , 
			{
				'id': 1,
				'category': 1,
				'name': '科班出身的MVC網頁開發：使用Python+Django',
				'description': '書中內容來自於團隊實際專案開發經驗和相關知識按系統撰寫而成。',
				'image': None ,
				'stock': 10,
				'price': 550,
				'owner': 'jacob'
			} 
		)
		
	def test_AnonymousUser_put(self): #測試未驗證的user使用put method
		response = self.client.put('/apis/product/1/' , 
			{
				'id': 1,
				'category': 1,
				'name': '科班出身的MVC網頁開發：使用Python+Django',
				'description': '書中內容來自於團隊實際專案開發經驗和相關知識按系統撰寫而成，put http method test。',
				'image': None ,
				'stock': 10,
				'price': 550,
				'owner': 'jacob'
			}
		)
		
		self.assertEqual(response.status_code , 401)
	
	def test_AnonymousUser_delete(self): #測試未驗證的user使用delete method
		response = self.client.delete('/apis/product/1/')
		
		self.assertEqual(response.status_code , 401)
		
	def test_AuthenticatedUser_get(self): #測試已驗證的user使用get method
		JWT = self.get_JSON_Web_Token()
		
		##建立有Authorization: Bearer + access token的header的Client() instance，完成post method
		c = Client(HTTP_AUTHORIZATION='Bearer ' + JWT['access'])
		response = c.get('/apis/product/1/')
		
		self.assertEqual(response.status_code , 200)
		self.assertEqual(response.data , 
			{
				'id': 1,
				'category': 1,
				'name': '科班出身的MVC網頁開發：使用Python+Django',
				'description': '書中內容來自於團隊實際專案開發經驗和相關知識按系統撰寫而成。',
				'image': None ,
				'stock': 10,
				'price': 550,
				'owner': 'jacob'
			} 
		)
		
	def test_AuthenticatedUser_put(self): #測試已驗證的user使用get method
		JWT = self.get_JSON_Web_Token()
		
		##建立有Authorization: Bearer + access token的header的Client() instance
		c = Client(HTTP_AUTHORIZATION='Bearer ' + JWT['access'])
		response = c.put('/apis/product/1/' , 
			{
				'category': 1,
				'name': '科班出身的MVC網頁開發：使用Python+Django',
				'description': '書中內容來自於團隊實際專案開發經驗和相關知識按系統撰寫而成，put http method test。',
				#'image': None ,
				'stock': 10,
				'price': 550
			}
			,content_type='application/json'
		)
		
		self.assertEqual(response.status_code , 200)
		self.assertEqual(response.data , 
			{
				'id': 1,
				'category': 1,
				'name': '科班出身的MVC網頁開發：使用Python+Django',
				'description': '書中內容來自於團隊實際專案開發經驗和相關知識按系統撰寫而成，put http method test。',
				'image': None ,
				'stock': 10,
				'price': 550,
				'owner': 'jacob'
			}
		)