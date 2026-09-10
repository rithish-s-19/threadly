from django.db import models
from django.contrib.auth.models import User
import json

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Unisex', 'Unisex'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Unisex')
    
    # Store available colors and sizes as comma-separated strings for simplicity
    available_colors = models.CharField(max_length=200, help_text="Comma-separated (e.g. Black, White, Grey)")
    available_sizes = models.CharField(max_length=200, help_text="Comma-separated (e.g. S, M, L, XL)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_colors_list(self):
        return [c.strip() for c in self.available_colors.split(',') if c.strip()]

    def get_sizes_list(self):
        return [s.strip() for s in self.available_sizes.split(',') if s.strip()]

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=150, default='')
    email = models.EmailField(default='')
    phone = models.CharField(max_length=20, default='')
    address = models.TextField()
    city = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=100, default='')
    pincode = models.CharField(max_length=20, default='')
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.full_name or self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50)
    custom_text = models.CharField(max_length=200, blank=True, null=True)
    text_position = models.CharField(max_length=50, blank=True, null=True)
    text_size = models.CharField(max_length=50, blank=True, null=True)
    design = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_cost(self):
        return self.product.price * self.quantity
