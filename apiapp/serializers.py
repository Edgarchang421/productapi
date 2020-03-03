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
		