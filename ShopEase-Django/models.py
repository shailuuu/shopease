from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)
    image = models.URLField(blank=True)
    class Meta: verbose_name_plural = 'categories'; ordering = ['name']
    def __str__(self): return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text='Optional remote placeholder image')
    brand = models.CharField(max_length=80, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)
    best_seller = models.BooleanField(default=False)
    class Meta: ordering = ['-created_at']
    def __str__(self): return self.name
    @property
    def selling_price(self): return self.discount_price if self.discount_price else self.price
    @property
    def discount_percent(self):
        return int((self.price - self.selling_price) / self.price * 100) if self.discount_price else 0
    def get_absolute_url(self): return reverse('product_detail', args=[self.slug])

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"{self.user}'s cart"
    @property
    def total(self): return sum((item.subtotal for item in self.items.select_related('product')), Decimal('0'))
    @property
    def savings(self): return sum((item.savings for item in self.items.select_related('product')), Decimal('0'))

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    class Meta: unique_together = ('cart', 'product')
    @property
    def subtotal(self): return self.product.selling_price * self.quantity
    @property
    def savings(self): return (self.product.price - self.product.selling_price) * self.quantity

class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, blank=True, related_name='wishlisted_by')
    def __str__(self): return f"{self.user}'s wishlist"

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=120); email = models.EmailField(); mobile = models.CharField(max_length=20)
    address = models.TextField(); city = models.CharField(max_length=80); state = models.CharField(max_length=80); pincode = models.CharField(max_length=12)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.name} - {self.city}'

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING='Pending'; CONFIRMED='Confirmed'; PROCESSING='Processing'; SHIPPED='Shipped'; DELIVERED='Delivered'; CANCELLED='Cancelled'
    class Payment(models.TextChoices): PENDING='Pending'; COD='Cash on Delivery'
    order_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(max_length=20, choices=Payment.choices, default=Payment.COD)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']
    def save(self, *args, **kwargs):
        if not self.order_id:
            from uuid import uuid4
            self.order_id = f'SE-{uuid4().hex[:10].upper()}'
        super().save(*args, **kwargs)
    def __str__(self): return self.order_id

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=180)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    @property
    def subtotal(self): return self.unit_price * self.quantity
