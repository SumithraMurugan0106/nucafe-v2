import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import json
import time
from sqlalchemy import func
from rapidfuzz import fuzz, process
# Ensure MenuItem is imported from your database file
from database import Session, User, Order, MenuItem, hash_password, check_password

# --- 1. CONFIG ---
# Replace that "keyboard_double" line with a clean header
st.set_page_config(page_title="NuCafe", page_icon="☕", layout="wide")

# Use this for a clean, centered title
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>NuCafe Digital Menu</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Fresh Food • Fast Delivery • Fine Taste</p>", unsafe_allow_html=True)
def search_menu(query, menu_items):
    names = [item.name for item in menu_items]

    results = process.extract(query, names, limit=5)

    matched_items = []
    for name, score, _ in results:
        if score > 60:
            matched_items.append(name)

    return matched_items

# --- 2. PREMIUM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Apply font and background safely */
    .dna-match {
        background: rgba(229, 9, 20, 0.1);
        color: #E50914;
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    .stApp {
        font-family: 'Poppins', sans-serif;
        background-color: #0F0F0F;
    }

    /* Section Titles with that Red Accent */
    .section-title { 
        font-size: 1.8rem; 
        font-weight: 700; 
        margin: 20px 0; 
        color: #FFFFFF; 
        border-left: 5px solid #E50914; 
        padding-left: 15px; 
    }

    /* Menu Card Styles */
    .classic-card { 
        background: #1A1A1A; 
        border-radius: 15px; 
        transition: transform 0.3s ease, border-color 0.3s ease; 
        border: 1px solid #2A2A2A; 
        padding: 0px;
        overflow: hidden;
    }
    .classic-card:hover { 
        transform: translateY(-5px); 
        border-color: #E50914; 
        box-shadow: 0 10px 20px rgba(229, 9, 20, 0.2); 
    }

    /* Image Container Fix */
    .img-container img { 
        width: 100%; 
        height: 180px; 
        object-fit: cover;
        border-radius: 15px 15px 0 0;
    }

    /* Typography inside cards */
    .food-name { font-size: 1.1rem; font-weight: 600; color: white; padding: 10px 15px 0 15px; }
    .food-price { color: #FFB800; font-weight: 700; font-size: 1.2rem; padding: 0 15px 15px 15px; }

    /* FIX: The Sidebar Toggle Button */
    /* Hide the 'Made with Streamlit' footer */
    footer {visibility: hidden;}

    /* Only hide the top right menu, NOT the sidebar toggle icon */
    [data-testid="stHeader"] {
        background: transparent;
    }
    
    /* Ensure the toggle button is visible and colored red to stand out */
    [data-testid="collapsedControl"] {
        color: #E50914 !important; 
        visibility: visible !important;
    }
</style>
""", unsafe_allow_html=True)


# --- 3. HELPER FUNCTIONS ---
@st.cache_resource
def load_data():
    with Session() as db:
        items = db.query(MenuItem).all()
        df = pd.DataFrame([
            {"food_name": i.food_name, "category": i.category, "price": i.price, "image": i.image, "is_veg": getattr(i, 'is_veg', True)} 
            for i in items
        ])
    # Load AI Brain
    try:
        with open('simple_data.pkl', 'rb') as f:
            brain = pickle.load(f)
    except:
        brain = None
    return df, brain

menu_df, ai = load_data()
all_items = menu_df['food_name'].tolist()

def get_all_scores(user_id):
    if ai is None: return {name: 50 for name in all_items}
    u_idx = (user_id or 0) % 1000
    user_vec = ai['P'][u_idx]
    scores = np.dot(ai['Q'], user_vec)
    final = np.clip(scores * 100, 45, 99).astype(int)
    return {name: final[idx] for name, idx in ai['food_to_idx'].items()}
def get_complementary_recommendations(cart_items):
    if not cart_items:
        return []
    
    with Session() as db:
        # Find all orders that contain items currently in our cart
        related_orders = db.query(Order.user_id, Order.food_name).filter(
            Order.food_name.in_(cart_items)
        ).all()
        
        user_ids = [o.user_id for o in related_orders]
        
        # Find WHAT ELSE those same users bought in their history
        suggestions = db.query(Order.food_name, func.count(Order.id)).filter(
            Order.user_id.in_(user_ids),
            Order.food_name.notin_(cart_items) # Don't suggest what's already in cart
        ).group_by(Order.food_name).order_by(func.count(Order.id).desc()).limit(3).all()
        
        return [s[0] for s in suggestions]

# --- 4. AUTHENTICATION ---
if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.markdown("<br><br><div class='auth-header'>NuCafé</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        with st.container(border=True):
            tab1, tab2 = st.tabs(["Sign In", "New Account"])
            with tab1:
                u = st.text_input("Username", key="login_u")
                p = st.text_input("Password", type="password", key="login_p")
                if st.button("Sign In", width='stretch', type="primary"):
                    with Session() as db:
                        user = db.query(User).filter_by(username=u).first()
                        if user and check_password(p, user.password):
                            st.session_state.user_id, st.session_state.username = user.id, u
                            st.session_state.cart = {}
                            st.rerun()
                        else: st.error("Invalid Credentials")
            with tab2:
                nu = st.text_input("Choose Username", key="reg_u")
                npwd = st.text_input("Choose Password", type="password", key="reg_p")
                if st.button("Create Account", width='stretch'):
                    with Session() as db:
                        if db.query(User).filter_by(username=nu).first(): st.error("Username taken!")
                        else:
                            db.add(User(username=nu, password=hash_password(npwd)))
                            db.commit()
                            st.success("Success! You can now Sign In.")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    # 👑 User Profile Section
    st.markdown(f"### 👑 Welcome, **{st.session_state.username.capitalize()}**")
    st.divider()
    
    # 🧬 Taste DNA Chart (Visual Cleanup)
    st.markdown("#### 🧬 Your Taste DNA")
    with Session() as db:
        user_orders = db.query(Order.category).filter_by(user_id=st.session_state.user_id).all()
        if user_orders:
            dna_data = pd.Series([o[0] for o in user_orders]).value_counts()
            # Reduced height to prevent sidebar scrolling too much
            st.bar_chart(dna_data, color="#E50914", height=150)
        else:
            st.info("DNA building in progress... Order something! 🍽️")
    
    st.divider()

    # 🛒 Your Order (Cart)
    st.markdown("#### 🛒 Your Order")
    if not st.session_state.get('cart'):
        st.caption("Plate is empty. Start adding items! 🍛")
    else:
        total = 0
        current_cart_names = list(st.session_state.cart.keys())
        
        # Display items in cart with better spacing
        for name, info in list(st.session_state.cart.items()):
            item_total = info['price'] * info['qty']
            total += item_total
            
            # Using st.expander or simple rows to avoid tiny cramped columns
            with st.container():
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{name}** (x{info['qty']})")
                if c2.button("🗑️", key=f"remove_{name}"):
                    if info['qty'] > 1:
                        st.session_state.cart[name]['qty'] -= 1
                    else:
                        del st.session_state.cart[name]
                    st.rerun()
                st.caption(f"Price: ₹{int(item_total)}")

        st.markdown(f"### Total: ₹{int(total)}")

        # --- SMART RECOMMENDATIONS ---
        recs = get_complementary_recommendations(current_cart_names)
        if recs:
            st.markdown("---")
            st.markdown("##### 🍟 Pair it with...")
            for rec_name in recs:
                item_data = menu_df[menu_df['food_name'] == rec_name]
                if not item_data.empty:
                    item_info = item_data.iloc[0]
                    # Vertical layout for recs looks better in a narrow sidebar
                    col_rec1, col_rec2 = st.columns([3, 1])
                    with col_rec1:
                        st.write(f"{rec_name} (₹{int(item_info['price'])})")
                    with col_rec2:
                        if st.button("➕", key=f"rec_{rec_name}"):
                            st.session_state.cart[rec_name] = {
                                'price': float(item_info['price']), 
                                'qty': 1, 
                                'category': str(item_info['category'])
                            }
                            st.rerun()

        # Big Action Button
        if st.button("PROCEED TO PAY", use_container_width=True, type="primary"):
            with Session() as db:
                for name, info in st.session_state.cart.items():
                    for _ in range(info['qty']):
                        db.add(Order(user_id=st.session_state.user_id, food_name=name, category=info['category'], price=info['price']))
                db.commit()
            st.session_state.cart = {}
            st.success("Order Placed! 🎉")
            st.rerun()

    # 📜 Grouped History (Visual Cleanup)
    st.divider()
    st.markdown("#### 📜 Recent Orders")
    with Session() as db:
        history_data = db.query(
            Order.food_name, Order.price, Order.category, func.count(Order.id).label('qty')
        ).filter_by(user_id=st.session_state.user_id).group_by(
            Order.food_name, Order.price, Order.category
        ).order_by(func.max(Order.id).desc()).limit(5).all() # Limited to 5 for cleanliness
        
        if history_data:
            # Container with fixed height for scrolling history
            with st.container(height=250):
                for name, price, cat, qty in history_data:
                    st.markdown(f"""
                    <div style="background: #1A1A1A; border-radius: 8px; padding: 10px; margin-bottom: 8px; border-left: 3px solid #E50914;">
                        <div style="color: white; font-weight: 600; font-size: 0.9rem;">{name} <span style="color: #46D369;">x{qty}</span></div>
                        <div style="color: #888; font-size: 0.75rem;">₹{int(price)} | {cat}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Reorder {name}", key=f"re_{name}_{qty}", use_container_width=True):
                        st.session_state.cart[name] = {'price': float(price), 'qty': 1, 'category': str(cat)}
                        st.rerun()
        else:
            st.caption("No history yet.")

    # Sign Out at the very bottom
    if st.button("Sign Out", use_container_width=True):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
# --- 6. MAIN CONTENT ---

# Search & Diet Filter
# --- 6. MAIN CONTENT ---
# --- HELPER SECTION (Top of app.py) ---
def get_predicted_wait_time(base_prep_time, category):
    with Session() as db:
        # 1. Count active orders in the last 30 mins
        # (Assuming orders are cleared eventually; for now, we count recent entries)
        active_orders_count = db.query(Order).count()
        
        # 2. Kitchen Load Factor (1.5 min delay per 5 active orders)
        load_penalty = (active_orders_count // 5) * 1.5
        
        # 3. Complexity Multiplier
        # Biryani/Main Course takes longer to scale than Beverages/Snacks
        complexity_map = {
            "Biryani": 1.5,      # Heavy load impact
            "Fastfood": 1.2,     # Moderate impact
            "South Indian": 1.1, # Fast turnover
            "Beverage": 0.8      # Very fast, barely affected by food load
        }
        multiplier = complexity_map.get(category, 1.0)
        
        predicted_time = (base_prep_time + load_penalty) * multiplier
        return int(predicted_time)

# --- MAIN CONTENT SECTION ---
# --- 6. MAIN CONTENT ---

# 1. SEARCH & DIETARY FILTER UI
# Define the reset function for the home button
def reset_home():
    st.session_state.main_search = ""

st.markdown("<h1 style='color:#E50914; margin-bottom:0;'>NuCafé</h1>", unsafe_allow_html=True)

col_search, col_veg, col_home = st.columns([3, 1, 0.5])

with col_search:
    search_query = st.text_input(
        "🔍 Search...", 
        placeholder="Biryani, Coffee...", 
        label_visibility="collapsed", 
        key="main_search"
    )

with col_veg:
    # DEFINING diet_pref HERE so it is available for the logic below
    diet_pref = st.radio("Diet", ["All", "Veg Only"], horizontal=True, label_visibility="collapsed")

with col_home:
    if search_query:
        st.button("🏠", on_click=reset_home, help="Back to Home")

# 2. FILTERING LOGIC 
# This now works because diet_pref is defined above
display_df = menu_df.copy()
if diet_pref == "Veg Only":
    display_df = display_df[display_df['is_veg'] == True]

# 3. DYNAMIC RENDER FUNCTION
def render_classic_row(title, item_names, is_trending=False):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    if not item_names:
        st.caption("Nothing to show here.")
        return

    score_map = get_all_scores(st.session_state.get('user_id', 0))
    
    # Grid Layout
    for i in range(0, len(item_names), 4):
        cols = st.columns(4)
        batch = item_names[i : i + 4]
        
        for idx, name in enumerate(batch):
            item_data = display_df[display_df['food_name'] == name]
            if item_data.empty: continue
            row = item_data.iloc[0]
            
            match = score_map.get(name, 50)
            
            with cols[idx]:
                # PREDICTED WAIT TIME LOGIC
                # Fixed: Changed row.get('prep_time', 15) to ensure it pulls from the DB
                base_time = row.get('prep_time', 15)
                real_time = get_predicted_wait_time(base_time, row['category'])
                time_color = "#46D369" if real_time <= 15 else "#FFB800" if real_time <= 25 else "#E50914"

                st.markdown(f"""
                    <div class="classic-card">
                        <div style="padding: 10px; display: flex; justify-content: space-between;">
                            <span style="color: {time_color}; font-weight: bold; font-size: 0.75rem;">⏱️ {real_time} mins</span>
                            <span class="dna-match">{'🔥 Trending' if is_trending else f'⭐ {match}% Match'}</span>
                        </div>
                        <div class="img-container"><img src="{row['image']}"></div>
                        <div class="card-meta">
                            <div class="food-name">{name}</div>
                            <div class="food-price">₹{int(row['price'])}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Add to Plate", key=f"btn_{title}_{name}_{i}_{idx}"):
                    if name in st.session_state.cart:
                        st.session_state.cart[name]['qty'] += 1
                    else:
                        st.session_state.cart[name] = {
                            'price': float(row['price']), 
                            'qty': 1, 
                            'category': str(row['category'])
                        }
                    st.toast(f"✅ {name} added!")
                    st.rerun()

# 4. DISPLAY LOGIC
if search_query:
    food_list = display_df['food_name'].tolist()
    matches = process.extract(search_query, food_list, scorer=fuzz.WRatio, limit=10)
    search_results = [match[0] for match in matches if match[1] > 60]

    if search_results:
        render_classic_row(f"Results for '{search_query}'", search_results)
    else:
        st.warning("No matches found.")
else:
    # Row 1: Trending
    with Session() as db:
        trending_data = db.query(Order.food_name, func.count(Order.id)).group_by(Order.food_name).order_by(func.count(Order.id).desc()).limit(10).all()
        trending_list = [t[0] for t in trending_data if t[0] in display_df['food_name'].values][:4]
    
    if trending_list:
        render_classic_row("🔥 Trending Now", trending_list, is_trending=True)

    # Row 2: DNA Handpicked
    score_map = get_all_scores(st.session_state.user_id)
    dna_picks = [x for x in all_items if x in display_df['food_name'].values]
    dna_picks = sorted(dna_picks, key=lambda x: score_map.get(x, 0), reverse=True)
    # Filter out items already in trending to keep it fresh
    filtered_dna = [x for x in dna_picks if x not in trending_list][:12]
    render_classic_row("✨ Handpicked for Your DNA", filtered_dna)

    # Row 3: Category Explore
    st.markdown("<div class='section-title'>🔍 Explore Categories</div>", unsafe_allow_html=True)
    all_categories = sorted(display_df['category'].unique().tolist())
    selected_categories = st.multiselect("Select categories to view", options=all_categories)
    for cat in selected_categories:
        cat_items = display_df[display_df['category'] == cat]['food_name'].tolist()
        render_classic_row(f"🏛️ {cat}", cat_items)