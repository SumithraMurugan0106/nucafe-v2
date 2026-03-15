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
st.set_page_config(layout="wide", page_title="NuCafé Premium", page_icon="🍽️")
def get_predicted_wait_time(base_prep_time):
    with Session() as db:
        # Count total active/recent orders in the last 30 mins to estimate kitchen load
        # For this simplified version, we'll just count total orders in the DB
        active_orders_count = db.query(Order).count()
        
        # Load Factor: Add 2 minutes for every 5 active orders
        load_penalty = (active_orders_count // 5) * 2
        
        predicted_time = base_prep_time + load_penalty
        return predicted_time
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
    html, body, [class*="st-"] { font-family: 'Poppins', sans-serif; background-color: #0F0F0F; }
    
    /* Menu Card Styles */
    .section-title { font-size: 1.8rem; font-weight: 700; margin: 40px 0 20px 0; color: #FFFFFF; border-left: 5px solid #E50914; padding-left: 15px; }
    .classic-card { background: #1A1A1A; border-radius: 15px; transition: 0.3s; border: 1px solid #2A2A2A; margin-bottom: 10px; height: 100%; }
    .classic-card:hover { transform: translateY(-5px); border-color: #E50914; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
    .img-container { width: 100%; height: 180px; border-radius: 15px 15px 0 0; overflow: hidden; }
    .img-container img { width: 100%; height: 100%; object-fit: cover; }
    .card-meta { padding: 15px; }
    .food-name { font-size: 1.1rem; font-weight: 600; color: white; margin-bottom: 5px; }
    .food-price { color: #FFB800; font-weight: 700; font-size: 1rem; }
    
   /* Totally removes the text artifact while keeping the sidebar functionality */
[data-testid="collapsedControl"] {
    text-indent: -9999px;
    white-space: nowrap;
}

[data-testid="collapsedControl"]::after {
    content: "☰"; 
    text-indent: 0;
    float: left;
    color: white;
    font-size: 28px;
    margin-left: 10px;
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

def render_classic_row(title, foods, is_trending=False):
    if not foods: return
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    
    score_map = get_all_scores(st.session_state.get('user_id', 0))
    
    # Process items in batches of 4 to create a grid
    for i in range(0, len(foods), 4):
        cols = st.columns(4)
        batch = foods[i : i + 4]
        
        for idx, name in enumerate(batch):
            item_data = menu_df[menu_df['food_name'] == name]
            if item_data.empty: continue
            item = item_data.iloc[0]
            match = score_map.get(name, 50)
            
            with cols[idx]:
                st.markdown(f"""
                    <div class="classic-card">
                        <div class="img-container"><img src="{item['image']}"></div>
                        <div class="card-meta">
                            <span class="dna-match">{'🔥 Trending' if is_trending else f'⭐ {match}% DNA Match'}</span>
                            <div class="food-name">{name}</div>
                            <div class="food-price">₹{int(item['price'])}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Add to Plate", key=f"add_{name}_{title}_{i}_{idx}", width='stretch'):
                    if name in st.session_state.cart:
                        st.session_state.cart[name]['qty'] += 1
                    else:
                        st.session_state.cart[name] = {
                            'price': float(item['price']), 
                            'qty': 1, 
                            'category': str(item['category'])
                        }
                    st.toast(f"✅ {name} added!")
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
    st.markdown(f"### 👑 Welcome, {st.session_state.username}")
    
    # 🧬 Taste DNA Chart
    st.markdown("#### 🧬 Your Taste DNA")
    with Session() as db:
        user_orders = db.query(Order.category).filter_by(user_id=st.session_state.user_id).all()
        if user_orders:
            dna_data = pd.Series([o[0] for o in user_orders]).value_counts()
            st.bar_chart(dna_data, color="#E50914")
        else:
            st.caption("DNA building in progress...")
    
    # 🛒 Your Order (Cart)
    st.markdown("#### 🛒 Your Order")
    if not st.session_state.get('cart'):
        st.caption("Plate is empty. Start adding items! 🍛")
    else:
        total = 0
        current_cart_names = list(st.session_state.cart.keys())
        
        # Display items in cart
        for name, info in list(st.session_state.cart.items()):
            item_total = info['price'] * info['qty']
            total += item_total
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"**{name}** (x{info['qty']})")
                st.caption(f"₹{int(item_total)}")
            with c2:
                if st.button("🗑️", key=f"remove_{name}"):
                    if info['qty'] > 1:
                        st.session_state.cart[name]['qty'] -= 1
                    else:
                        del st.session_state.cart[name]
                    st.rerun()

        st.markdown(f"### Total: ₹{int(total)}")

        # --- SMART RECOMMENDATIONS (The Solution) ---
        recs = get_complementary_recommendations(current_cart_names)
        if recs:
            st.markdown("---")
            st.markdown("##### 🍟 Pair it with...")
            for rec_name in recs:
                # Check if item exists in menu to avoid IndexError
                item_data = menu_df[menu_df['food_name'] == rec_name]
                if not item_data.empty:
                    item_info = item_data.iloc[0]
                    col_rec1, col_rec2 = st.columns([3, 1])
                    with col_rec1:
                        st.write(f"**{rec_name}**")
                        st.caption(f"₹{int(item_info['price'])}")
                    with col_rec2:
                        if st.button("➕", key=f"rec_{rec_name}"):
                            st.session_state.cart[rec_name] = {
                                'price': float(item_info['price']), 
                                'qty': 1, 
                                'category': str(item_info['category'])
                            }
                            st.rerun()

        if st.button("PROCEED TO PAY", width='stretch', type="primary"):
            with Session() as db:
                for name, info in st.session_state.cart.items():
                    for _ in range(info['qty']):
                        db.add(Order(user_id=st.session_state.user_id, food_name=name, category=info['category'], price=info['price']))
                db.commit()
            st.session_state.cart = {}
            st.success("Order Placed! 🎉")
            st.rerun()

    # 📜 Grouped History
    st.markdown("---")
    st.markdown("#### 📜 Recent Orders")
    with Session() as db:
        history_data = db.query(
            Order.food_name, Order.price, Order.category, func.count(Order.id).label('qty')
        ).filter_by(user_id=st.session_state.user_id).group_by(
            Order.food_name, Order.price, Order.category
        ).order_by(func.max(Order.id).desc()).limit(10).all()
        
        if history_data:
            with st.container(height=300):
                for name, price, cat, qty in history_data:
                    st.markdown(f"""
                    <div style="background: #1A1A1A; border-radius: 10px; padding: 12px; margin-bottom: 5px; border-left: 4px solid #E50914;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: white; font-weight: 600;">{name}</span>
                            <span style="color: #46D369; font-size: 0.8rem;">x{qty}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #888; font-size: 0.8rem;">{cat}</span>
                            <span style="color: #FFB800; font-weight: 700;">₹{int(price)}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Reorder {name}", key=f"re_{name}_{qty}"):
                        st.session_state.cart[name] = {'price': float(price), 'qty': 1, 'category': str(cat)}
                        st.rerun()
        else:
            st.caption("No history yet.")

    if st.button("Sign Out", width='stretch'):
        st.session_state.user_id = None
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