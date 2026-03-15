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
    data = [
        {"food_name": "Hyderabadi Chicken Biryani", "category": "Biryani", "price": 280, "prep_time": 25, "is_veg": False, 
         "image": "https://images.unsplash.com/photo-1563379091339-03b21bc4a4f8?w=600"},
        {"food_name": "Paneer Tikka Biryani", "category": "Biryani", "price": 240, "prep_time": 20, "is_veg": True, 
         "image": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=600"},
        {"food_name": "Ghee Roast Dosa", "category": "South Indian", "price": 120, "prep_time": 10, "is_veg": True, 
         "image": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=600"},
        {"food_name": "Classic Veg Burger", "category": "Fastfood", "price": 150, "prep_time": 12, "is_veg": True, 
         "image": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=600"},
        {"food_name": "Masala Chai", "category": "Beverage", "price": 40, "prep_time": 5, "is_veg": True, 
         "image": "https://images.unsplash.com/photo-1571935443242-c1a1a79aa7c8?w=600"}
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