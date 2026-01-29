import streamlit as st
import pandas as pd
import time
import os
import requests
from streamlit_lottie import st_lottie

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="ITQAN Premium Office",
    layout="wide",
    page_icon="☕"
)

# اسم ملف البيانات
DATA_FILE = "orders.csv"

# 2. روابط أنيميشن عالية الجودة
ANIMATIONS = {
    "coffee": "https://lottie.host/57520e5d-168a-493f-998a-78536f901a1c/vO89TOn60r.json",
    "tea": "https://lottie.host/36979607-1603-4c55-83e9-9bc77a76046e/8n9xLAnX1E.json",
    "water": "https://lottie.host/9f5033c7-3135-4309-883a-48d6139c2357/3nOqD2S0vX.json",
    "food": "https://lottie.host/62635904-8994-47a7-897d-606d1531e842/IEnf3m9u1h.json",
    "default": "https://lottie.host/91106093-f111-477d-810a-706f85108f97/Bsc7H0XQkR.json"
}

@st.cache_data(ttl=600)
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def get_anim_by_order(order_text):
    if not isinstance(order_text, str):
        return load_lottieurl(ANIMATIONS["default"])
    
    text = order_text.lower()
    url = ANIMATIONS["default"]
    
    if any(x in text for x in ["قهوة", "coffee", "نسكافيه", "اسبريسو", "latte"]):
        url = ANIMATIONS["coffee"]
    elif any(x in text for x in ["شاي", "tea", "ينسون", "نعناع", "حلبه"]):
        url = ANIMATIONS["tea"]
    elif any(x in text for x in ["ميه", "ماء", "مياه", "water"]):
        url = ANIMATIONS["water"]
    elif any(x in text for x in ["اكل", "غدا", "ساندوتش", "food", "فطار"]):
        url = ANIMATIONS["food"]
        
    return load_lottieurl(url)

# 3. إدارة البيانات
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=["Time", "Name", "Room", "Order", "Status"])
    try:
        return pd.read_csv(DATA_FILE, encoding='utf-8-sig')
    except:
        return pd.DataFrame(columns=["Time", "Name", "Room", "Order", "Status"])

def save_order(name, room, order):
    df = load_data()
    new_order = pd.DataFrame([{
        "Time": time.strftime("%I:%M %p"),
        "Name": name,
        "Room": room,
        "Order": order,
        "Status": "Pending"
    }])
    df = pd.concat([df, new_order], ignore_index=True)
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

def mark_done(index):
    df = load_data()
    if index in df.index:
        df.at[index, "Status"] = "Done"
        df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# 4. التصميم الاحترافي CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0b0d17, #1a1c2c); color: white; }
    .order-card {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #00ffcc;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        direction: rtl;
        text-align: right;
    }
    .big-font { font-size: 24px !important; font-weight: bold; color: #00ffcc; }
    .small-font { font-size: 15px !important; color: #bdc3c7; }
    .stButton>button { border-radius: 10px; background-color: #00ffcc; color: #0b0d17; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 5. القائمة الجانبية (إضافة طلب)
with st.sidebar:
    st.markdown("## 📥 إضافة طلب جديد")
    with st.form("request_form", clear_on_submit=True):
        u_name = st.text_input("الاسم")
        u_room = st.text_input("الروم")

        u_order = st.text_input("الأوردر")
        
        if st.form_submit_button("إرسال للأوفيس 🚀"):
            if u_name and u_order:
                save_order(u_name, u_room, u_order)
                st.success("وصل يا فنان!")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("اكتب بياناتك الأول!")

# 6. شاشة العرض الرئيسية
st.title("⚡ LIVE OFFICE MONITOR")
st.markdown("---")

df = load_data()
pending = df[df["Status"] == "Pending"].iloc[::-1]

if not pending.empty:
    for idx, row in pending.iterrows():
        col_content, col_action = st.columns([5, 1])
        
        with col_content:
            # هنا التعديل السحري لحل مشكلة الـ NoneType
            c_anim, c_txt = st.columns([1, 4])
            
            with c_anim:
                anim_data = get_anim_by_order(row['Order'])
                if anim_data is not None:
                    st_lottie(anim_data, height=100, key=f"anim_{idx}")
                else:
                    st.markdown("### 🔔") # إيموجي بديل في حالة فشل التحميل
            
            with c_txt:
                st.markdown(f"""
                <div class="order-card">
                    <div class="big-font">{row['Order']}</div>
                    <div class="small-font">👤 {row['Name']} | 📍 {row['Room']}</div>
                    <div style="color:gray; font-size:11px;">🕒 {row['Time']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col_action:
            st.write(" ") # تحسين المحاذاة
            if st.button("تـم ✅", key=f"btn_{idx}", use_container_width=True):
                mark_done(idx)
                st.toast(f"طلب {row['Name']} خلص!")
                time.sleep(0.5)
                st.rerun()
else:
    st.info("مفيش طلبات حالياً.. المطبخ رايق 🍃")

# 7. الأرشيف الصغير
with st.expander("📂 سجل آخر الطلبات"):
    done_df = df[df["Status"] == "Done"].tail(10)
    st.dataframe(done_df[["Time", "Name", "Order"]], use_container_width=True)

# التحديث التلقائي
time.sleep(15)
st.rerun()