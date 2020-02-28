from django.db import models
from django.contrib.auth.models import User

#商品類別
class Category(models.Model):
	name = models.CharField(max_length=50); #類別名稱

	def __str__(self):
		return self.name

#商品資訊
class Product(models.Model):
	category = models.ForeignKey(Category , on_delete = models.CASCADE) #分類
	name = models.CharField(max_length = 50) #產品名稱
	description = models.TextField(default = '尚未有產品說明') #產品敘述
	image = models.ImageField(upload_to = 'media' , blank = True) #圖片
	stock = models.PositiveIntegerField(default = 0) #庫存
	price = models.PositiveIntegerField(default = 0) #價錢
	owner = models.ForeignKey(User , on_delete=models.CASCADE , related_name='products')

	def __str__(self):
		return self.name