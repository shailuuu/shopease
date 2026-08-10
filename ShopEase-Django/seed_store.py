from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product

class Command(BaseCommand):
    help = 'Creates sample ShopEase categories and products.'
    def handle(self, *args, **options):
        catalog = {
            'Electronics': [('Orbit Wireless Headphones', 'Aurora', 4999, 3999), ('Pulse Smart Watch', 'Nova', 6499, 5499), ('Canvas Bluetooth Speaker', 'Echo', 2999, None)],
            'Fashion': [('Linen Everyday Shirt', 'North', 2299, 1799), ('Classic Denim Jacket', 'North', 4599, 3899), ('Relaxed Cotton Tee', 'Form', 999, None)],
            'Accessories': [('Minimal Leather Wallet', 'Craft', 1499, None), ('Everyday Sunglasses', 'Sol', 1899, 1499), ('Weekender Canvas Bag', 'Craft', 3499, 2999)],
            'Home': [('Stoneware Coffee Set', 'Mellow', 2199, None), ('Soft Throw Blanket', 'Haven', 2799, 2299), ('Table Lamp No. 02', 'Haven', 3299, None)],
            'Books': [('The Art of Focus', 'Field Notes', 699, None), ('Designing Your Life', 'Field Notes', 799, 649), ('The Modern Kitchen', 'Page & Co', 1199, None)],
        }
        for category_name, products in catalog.items():
            category, _ = Category.objects.get_or_create(name=category_name, defaults={'slug': slugify(category_name), 'image': f'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=700&q=80'})
            for index, (name, brand, price, discount) in enumerate(products):
                Product.objects.get_or_create(slug=slugify(name), defaults={
                    'category': category, 'name': name, 'description': f'A carefully selected {name.lower()} made for everyday use. Quality materials and considered details.',
                    'price': price, 'discount_price': discount, 'brand': brand, 'stock_quantity': 12 + index * 4, 'rating': 4.2 + index / 10,
                    'featured': index == 0, 'best_seller': index == 1, 'image_url': f'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=700&q=80',
                })
        self.stdout.write(self.style.SUCCESS('Sample catalog created.'))
