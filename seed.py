from sqlalchemy import text, Column, Integer, String, Float, Boolean, DateTime
import datetime
from database import Session, engine, Base

# We define a "Fresh" version of the model just for seeding
# This ensures Python 100% sees the prep_time column
class FreshMenuItem(Base):
    __tablename__ = 'menu_items'
    id = Column(Integer, primary_key=True)
    food_name = Column(String, unique=True)
    category = Column(String)
    price = Column(Float)
    image = Column(String)
    is_veg = Column(Boolean, default=True) 
    prep_time = Column(Integer, default=15)
    __table_args__ = {'extend_existing': True}

def reset_and_seed():
    print("🚀 Starting Clean Room Reset...")
    
    # 1. Drop and Recreate
# 1. Drop and Recreate
    with engine.connect() as conn:
        # We add 'execution_options' to ensure the drop happens immediately
        conn.execute(text("DROP TABLE IF EXISTS menu_items CASCADE;").execution_options(autocommit=True))
        conn.execute(text("DROP TABLE IF EXISTS orders CASCADE;").execution_options(autocommit=True))
        conn.commit()
    
    Base.metadata.create_all(engine)
    print("🏗️ Database schema recreated.")

    # 2. Data to insert
    # seed_data.py
    data = [
        # --- BIRYANI (10 items) ---
        {"food_name": "Hyderabadi Chicken Biryani", "category": "Biryani", "price": 280, "prep_time": 25, "is_veg": False, "image": "https://images.unsplash.com/photo-1563379091339-03b21bc4a4f8?w=600"},
        {"food_name": "Paneer Tikka Biryani", "category": "Biryani", "price": 240, "prep_time": 20, "is_veg": True, "image": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=600"},
        {"food_name": "Lucknowi Mutton Biryani", "category": "Biryani", "price": 350, "prep_time": 30, "is_veg": False, "image": "https://loremflickr.com/600/400/biryani,mutton?random=1"},
        {"food_name": "Egg Dum Biryani", "category": "Biryani", "price": 180, "prep_time": 15, "is_veg": False, "image": "https://loremflickr.com/600/400/biryani,egg?random=2"},
        {"food_name": "Ambur Chicken Biryani", "category": "Biryani", "price": 220, "prep_time": 20, "is_veg": False, "image": "https://loremflickr.com/600/400/biryani,chicken?random=3"},
        {"food_name": "Kolkata Veg Biryani", "category": "Biryani", "price": 190, "prep_time": 20, "is_veg": True, "image": "https://loremflickr.com/600/400/biryani,veg?random=4"},
        {"food_name": "Malabar Fish Biryani", "category": "Biryani", "price": 310, "prep_time": 25, "is_veg": False, "image": "https://loremflickr.com/600/400/biryani,fish?random=5"},
        {"food_name": "Mushroom Dum Biryani", "category": "Biryani", "price": 210, "prep_time": 18, "is_veg": True, "image": "https://loremflickr.com/600/400/biryani,mushroom?random=6"},
        {"food_name": "Prawns Biryani", "category": "Biryani", "price": 380, "prep_time": 25, "is_veg": False, "image": "https://loremflickr.com/600/400/biryani,prawn?random=7"},
        {"food_name": "Sindhi Biryani", "category": "Biryani", "price": 260, "prep_time": 25, "is_veg": False, "image": "https://loremflickr.com/600/400/biryani,spicy?random=8"},

        # --- SOUTH INDIAN (15 items) ---
        {"food_name": "Ghee Roast Dosa", "category": "South Indian", "price": 120, "prep_time": 10, "is_veg": True, "image": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=600"},
        {"food_name": "Masala Dosa", "category": "South Indian", "price": 110, "prep_time": 12, "is_veg": True, "image": "https://loremflickr.com/600/400/dosa,masala?random=9"},
        {"food_name": "Idli Sambar (2 pcs)", "category": "South Indian", "price": 60, "prep_time": 5, "is_veg": True, "image": "https://loremflickr.com/600/400/idli,sambar?random=10"},
        {"food_name": "Medu Vada (2 pcs)", "category": "South Indian", "price": 70, "prep_time": 8, "is_veg": True, "image": "https://loremflickr.com/600/400/vada,southindian?random=11"},
        {"food_name": "Onion Uttapam", "category": "South Indian", "price": 90, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/uttapam?random=12"},
        {"food_name": "Rava Dosa", "category": "South Indian", "price": 130, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/ravadosa?random=13"},
        {"food_name": "Appam with Stew", "category": "South Indian", "price": 160, "prep_time": 20, "is_veg": True, "image": "https://loremflickr.com/600/400/appam?random=14"},
        {"food_name": "Puri Bhaji", "category": "South Indian", "price": 100, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/puribhaji?random=15"},
        {"food_name": "Lemon Rice", "category": "South Indian", "price": 120, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/lemonrice?random=16"},
        {"food_name": "Curd Rice", "category": "South Indian", "price": 90, "prep_time": 5, "is_veg": True, "image": "https://loremflickr.com/600/400/curdrice?random=17"},
        {"food_name": "Set Dosa", "category": "South Indian", "price": 100, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/setdosa?random=18"},
        {"food_name": "Paper Plain Dosa", "category": "South Indian", "price": 140, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/paperdosa?random=19"},
        {"food_name": "Paniyaram (6 pcs)", "category": "South Indian", "price": 80, "prep_time": 12, "is_veg": True, "image": "https://loremflickr.com/600/400/paniyaram?random=20"},
        {"food_name": "Bisibelebath", "category": "South Indian", "price": 130, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/sambarrice?random=21"},
        {"food_name": "Podid Dosa", "category": "South Indian", "price": 115, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/podidosa?random=22"},

        # --- NORTH INDIAN / MAIN COURSE (15 items) ---
        {"food_name": "Butter Chicken", "category": "North Indian", "price": 320, "prep_time": 25, "is_veg": False, "image": "https://loremflickr.com/600/400/butterchicken?random=23"},
        {"food_name": "Paneer Butter Masala", "category": "North Indian", "price": 260, "prep_time": 20, "is_veg": True, "image": "https://loremflickr.com/600/400/paneer?random=24"},
        {"food_name": "Dal Makhani", "category": "North Indian", "price": 220, "prep_time": 30, "is_veg": True, "image": "https://loremflickr.com/600/400/dalmakhani?random=25"},
        {"food_name": "Chole Bhature", "category": "North Indian", "price": 160, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/cholebhature?random=26"},
        {"food_name": "Palak Paneer", "category": "North Indian", "price": 240, "prep_time": 20, "is_veg": True, "image": "https://loremflickr.com/600/400/palakpaneer?random=27"},
        {"food_name": "Kadhai Chicken", "category": "North Indian", "price": 300, "prep_time": 25, "is_veg": False, "image": "https://loremflickr.com/600/400/kadhaichicken?random=28"},
        {"food_name": "Mix Veg Curry", "category": "North Indian", "price": 180, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/mixveg?random=29"},
        {"food_name": "Aloo Gobhi", "category": "North Indian", "price": 150, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/aloogobhi?random=30"},
        {"food_name": "Garlic Naan", "category": "North Indian", "price": 50, "prep_time": 8, "is_veg": True, "image": "https://loremflickr.com/600/400/garlicnaan?random=31"},
        {"food_name": "Butter Roti", "category": "North Indian", "price": 25, "prep_time": 5, "is_veg": True, "image": "https://loremflickr.com/600/400/roti?random=32"},
        {"food_name": "Malai Kofta", "category": "North Indian", "price": 270, "prep_time": 25, "is_veg": True, "image": "https://loremflickr.com/600/400/malaikofta?random=33"},
        {"food_name": "Chicken Tikka Masala", "category": "North Indian", "price": 320, "prep_time": 25, "is_veg": False, "image": "https://loremflickr.com/600/400/chickentikka?random=34"},
        {"food_name": "Bhindi Do Pyaza", "category": "North Indian", "price": 170, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/bhindi?random=35"},
        {"food_name": "Jeera Rice", "category": "North Indian", "price": 110, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/jeerarice?random=36"},
        {"food_name": "Matar Paneer", "category": "North Indian", "price": 230, "prep_time": 20, "is_veg": True, "image": "https://loremflickr.com/600/400/matarpaneer?random=37"},

        # --- FASTFOOD (10 items) ---
        {"food_name": "Classic Veg Burger", "category": "Fastfood", "price": 150, "prep_time": 12, "is_veg": True, "image": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=600"},
        {"food_name": "Cheese Lava Burger", "category": "Fastfood", "price": 220, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/cheeseburger?random=38"},
        {"food_name": "Margherita Pizza", "category": "Fastfood", "price": 299, "prep_time": 20, "is_veg": True, "image": "https://loremflickr.com/600/400/pizza,margherita?random=39"},
        {"food_name": "Farmhouse Pizza", "category": "Fastfood", "price": 399, "prep_time": 20, "is_veg": True, "image": "https://loremflickr.com/600/400/pizza,veg?random=40"},
        {"food_name": "French Fries", "category": "Fastfood", "price": 99, "prep_time": 8, "is_veg": True, "image": "https://loremflickr.com/600/400/frenchfries?random=41"},
        {"food_name": "Peri Peri Fries", "category": "Fastfood", "price": 120, "prep_time": 8, "is_veg": True, "image": "https://loremflickr.com/600/400/periperi,fries?random=42"},
        {"food_name": "Chicken Nuggets (6 pcs)", "category": "Fastfood", "price": 160, "prep_time": 10, "is_veg": False, "image": "https://loremflickr.com/600/400/chickennuggets?random=43"},
        {"food_name": "Veg Grilled Sandwich", "category": "Fastfood", "price": 110, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/sandwich?random=44"},
        {"food_name": "Club Sandwich", "category": "Fastfood", "price": 180, "prep_time": 12, "is_veg": False, "image": "https://loremflickr.com/600/400/clubsandwich?random=45"},
        {"food_name": "Garlic Bread with Cheese", "category": "Fastfood", "price": 140, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/garlicbread?random=46"},

        # --- CHINESE (10 items) ---
        {"food_name": "Veg Hakka Noodles", "category": "Chinese", "price": 160, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/noodles?random=47"},
        {"food_name": "Chicken Fried Rice", "category": "Chinese", "price": 190, "prep_time": 15, "is_veg": False, "image": "https://loremflickr.com/600/400/friedrice?random=48"},
        {"food_name": "Gobi Manchurian Dry", "category": "Chinese", "price": 150, "prep_time": 12, "is_veg": True, "image": "https://loremflickr.com/600/400/gobimanchurian?random=49"},
        {"food_name": "Chilli Chicken", "category": "Chinese", "price": 240, "prep_time": 15, "is_veg": False, "image": "https://loremflickr.com/600/400/chillichicken?random=50"},
        {"food_name": "Spring Rolls (4 pcs)", "category": "Chinese", "price": 130, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/springrolls?random=51"},
        {"food_name": "Veg Momos Steamed", "category": "Chinese", "price": 100, "prep_time": 12, "is_veg": True, "image": "https://loremflickr.com/600/400/momos?random=52"},
        {"food_name": "Chicken Momos Fried", "category": "Chinese", "price": 140, "prep_time": 15, "is_veg": False, "image": "https://loremflickr.com/600/400/chickenmomos?random=53"},
        {"food_name": "Honey Chilli Potato", "category": "Chinese", "price": 160, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/honeychillipotato?random=54"},
        {"food_name": "Veg Manchurian Gravy", "category": "Chinese", "price": 180, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/manchurian?random=55"},
        {"food_name": "Schezwan Noodles", "category": "Chinese", "price": 170, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/schezwan?random=56"},

        # --- BEVERAGES (10 items) ---
        {"food_name": "Masala Chai", "category": "Beverage", "price": 40, "prep_time": 5, "is_veg": True, "image": "https://images.unsplash.com/photo-1571935443242-c1a1a79aa7c8?w=600"},
        {"food_name": "Cold Coffee", "category": "Beverage", "price": 120, "prep_time": 5, "is_veg": True, "image": "https://loremflickr.com/600/400/coldcoffee?random=57"},
        {"food_name": "Mango Lassi", "category": "Beverage", "price": 80, "prep_time": 5, "is_veg": True, "image": "https://loremflickr.com/600/400/mangolassi?random=58"},
        {"food_name": "Fresh Lime Soda", "category": "Beverage", "price": 60, "prep_time": 5, "is_veg": True, "image": "https://loremflickr.com/600/400/limesoda?random=59"},
        {"food_name": "Chocolate Milkshake", "category": "Beverage", "price": 140, "prep_time": 8, "is_veg": True, "image": "https://loremflickr.com/600/400/milkshake?random=60"},
        {"food_name": "Iced Tea", "category": "Beverage", "price": 90, "prep_time": 5, "is_veg": True, "image": "https://loremflickr.com/600/400/icedtea?random=61"},
        {"food_name": "Oreo Shake", "category": "Beverage", "price": 160, "prep_time": 8, "is_veg": True, "image": "https://loremflickr.com/600/400/oreoshake?random=62"},
        {"food_name": "Hot Chocolate", "category": "Beverage", "price": 130, "prep_time": 8, "is_veg": True, "image": "https://loremflickr.com/600/400/hotchocolate?random=63"},
        {"food_name": "Butter Milk", "category": "Beverage", "price": 50, "prep_time": 3, "is_veg": True, "image": "https://loremflickr.com/600/400/buttermilk?random=64"},
        {"food_name": "Mineral Water", "category": "Beverage", "price": 20, "prep_time": 1, "is_veg": True, "image": "https://loremflickr.com/600/400/waterbottle?random=65"},

        # --- DESSERTS (10 items) ---
        {"food_name": "Gulab Jamun (2 pcs)", "category": "Desserts", "price": 60, "prep_time": 5, "is_veg": True, "image": "https://loremflickr.com/600/400/gulabjamun?random=66"},
        {"food_name": "Rasmalai (2 pcs)", "category": "Desserts", "price": 90, "prep_time": 5, "is_veg": True, "image": "https://loremflickr.com/600/400/rasmalai?random=67"},
        {"food_name": "Sizzling Brownie", "category": "Desserts", "price": 180, "prep_time": 12, "is_veg": True, "image": "https://loremflickr.com/600/400/brownie?random=68"},
        {"food_name": "Vanilla Ice Cream", "category": "Desserts", "price": 70, "prep_time": 3, "is_veg": True, "image": "https://loremflickr.com/600/400/vanilla,icecream?random=69"},
        {"food_name": "Death by Chocolate", "category": "Desserts", "price": 220, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/chocolate,dessert?random=70"},
        {"food_name": "Gajar Ka Halwa", "category": "Desserts", "price": 110, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/gajarhalwa?random=71"},
        {"food_name": "Kulfi Falooda", "category": "Desserts", "price": 130, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/kulfi?random=72"},
        {"food_name": "Apple Pie", "category": "Desserts", "price": 160, "prep_time": 15, "is_veg": True, "image": "https://loremflickr.com/600/400/applepie?random=73"},
        {"food_name": "Fruit Salad with Cream", "category": "Desserts", "price": 140, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/fruitsalad?random=74"},
        {"food_name": "Moong Dal Halwa", "category": "Desserts", "price": 120, "prep_time": 10, "is_veg": True, "image": "https://loremflickr.com/600/400/dalhalwa?random=75"}
    ]

    # 3. Seed using the FreshMenuItem class
    with Session() as db:
        print("🌱 Seeding fresh data...")
        for item in data:
            new_item = FreshMenuItem(**item)
            db.add(new_item)
        db.commit()
        print("✅ Success! The menu is now correctly populated.")

if __name__ == "__main__":
    reset_and_seed()