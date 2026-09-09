import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'threadly.settings')
django.setup()

from store.models import Product

products = [
    {
        "name": "Classic Black Tee",
        "description": "A timeless classic black t-shirt made with 100% premium cotton.",
        "price": 499.00,
        "category": "Unisex",
        "available_colors": "Black, White, Grey",
        "available_sizes": "S, M, L, XL, XXL"
    },
    {
        "name": "Minimal White Tee",
        "description": "Clean, crisp, and comfortable. Your everyday white tee.",
        "price": 499.00,
        "category": "Unisex",
        "available_colors": "White, Black",
        "available_sizes": "S, M, L, XL"
    },
    {
        "name": "Urban Grey Tee",
        "description": "Perfect for the city. Neutral grey tone that goes with anything.",
        "price": 599.00,
        "category": "Men",
        "available_colors": "Grey, Black, Navy",
        "available_sizes": "M, L, XL, XXL"
    },
    {
        "name": "Navy Essential Tee",
        "description": "Deep navy blue for a slightly elevated casual look.",
        "price": 599.00,
        "category": "Unisex",
        "available_colors": "Navy, White",
        "available_sizes": "S, M, L, XL"
    },
    {
        "name": "Red Statement Tee",
        "description": "Stand out with our bold red statement t-shirt.",
        "price": 699.00,
        "category": "Women",
        "available_colors": "Red, Black, White",
        "available_sizes": "S, M, L"
    },
    {
        "name": "Everyday Oversized Tee",
        "description": "Relaxed fit for ultimate comfort. Streetwear inspired.",
        "price": 699.00,
        "category": "Unisex",
        "available_colors": "Black, Grey, Navy",
        "available_sizes": "M, L, XL, XXL"
    }
]

for p_data in products:
    Product.objects.get_or_create(name=p_data['name'], defaults=p_data)

print("Sample products populated successfully.")
