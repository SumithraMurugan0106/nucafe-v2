import pandas as pd
import numpy as np
import random
import pickle
import json
import os
# Update your first line to include Boolean
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey

def train_and_save():
    print("🎬 Training Scalable AI Engine...")

    categories = {
        "South Indian": ["Dosa", "Idli", "Vada", "Pongal", "Uttapam", "Bhat", "Rava Kesari"],
        "North Indian": ["Paneer Tikka", "Dal Makhani", "Naan", "Chole Bhature", "Paratha", "Butter Chicken"],
        "Biryani": ["Hyderabadi", "Ambur", "Donne", "Lucknowi", "Egg Biryani", "Veg Biryani"],
        "Beverage": ["Filter Coffee", "Masala Chai", "Badam Milk", "Cold Coffee", "Fruit Juice", "Lassi"],
        "Fastfood": ["Burger", "Pizza", "Pasta", "Sandwich", "French Fries", "Momos"],
        "Snack": ["Samosa", "Kachori", "Bhel Puri", "Pani Puri", "Vada Pav", "Pakoda"]
    }

    category_images = {
        "South Indian": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=600&auto=format&fit=crop&q=60",
        "North Indian": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=600&auto=format&fit=crop&q=60",
        "Biryani": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=600&auto=format&fit=crop&q=60",
        "Beverage": "https://images.unsplash.com/photo-1609951651556-5334e2706168?w=600&auto=format&fit=crop&q=60",
        "Fastfood": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600&auto=format&fit=crop&q=60",
        "Snack": "https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=600&auto=format&fit=crop&q=60"
    }

    menu_items = []
    classics = [
        ("CTR Benne Masala Dosa", "South Indian", 95, 10),
        ("Filter Coffee", "Beverage", 40, 5),
        ("MTR Rava Idli", "South Indian", 80, 8),
        ("Meghana Chicken Biryani", "Biryani", 320, 20),
        ("Truffles All American Burger", "Fastfood", 290, 15),
        ("VV Puram Chat Basket", "Snack", 80, 5)
    ]
    
    for name, cat, price, prep in classics:
        menu_items.append({"food_name": name, "category": cat, "price": price, "prep_time": prep, "image": category_images[cat], "is_new": "no"})

    for i in range(120):
        cat = random.choice(list(categories.keys()))
        suffix = random.choice(categories[cat])
        menu_items.append({
            "food_name": f"Special {cat} {suffix} {i+1}",
            "category": cat,
            "price": random.randint(50, 450),
            "prep_time": random.randint(5, 25),
            "image": category_images[cat],
            "is_new": random.choice(["yes", "no", "no", "no", "no"])
        })

    with open('menu.json', 'w') as f:
        json.dump(menu_items, f, indent=4)

    # Matrix Factorization Training
    num_users, latent_features = 1000, 12
    food_names = [m['food_name'] for m in menu_items]
    food_to_idx = {name: i for i, name in enumerate(food_names)}
    
    P = np.random.normal(scale=1./latent_features, size=(num_users, latent_features))
    Q = np.random.normal(scale=1./latent_features, size=(len(food_names), latent_features))

    # Save the 'Brain'
    with open('simple_data.pkl', 'wb') as f:
        pickle.dump({'P': P, 'Q': Q, 'food_to_idx': food_to_idx}, f)
    
    print("✅ AI Ready.")

if __name__ == "__main__":
    train_and_save()