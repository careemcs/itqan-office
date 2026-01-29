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

# أسماء الملفات
DATA_FILE = "orders.csv"
USERS_FILE = "users.csv"

# 2. روابط الأنيميشن
ANIMATIONS = {
    "coffee": "https://lottie.host/57520e5d-168a-493f-998a-78536f901a1c/vO89TOn60r.json",
    "tea": "https://lottie.host/36979607-1603-4c55-83e9-9bc77a76046e/8n9xLAnX1E.json",
    "water": "https://lottie.host/9f5033c7-3135-4309-883a-48d6139c2357/3nOqD2S0vX.json",
    "food": "https://lottie.host/62635904-8994-47a7-897d-606d1531e842/IEnf3m9u1h.json",
    "default": "https://lottie.host/91106093-f111-477d-810a-706f85108f97/Bsc7H0XQkR.json",
    "login": "https://lottie.host/4b82d733-4050-4d51-aa3f-8df95cbdf356/M6q3s7Z0g2.json" # أنيميشن للدخول
}

@st.cache_data(ttl=600)
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=3)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def get_anim_by_order(order_text):
    if not isinstance(order_text, str): return load_lottieurl(ANIMATIONS["default"])
    text = order_text.lower()
    url = ANIMATIONS["default"]
    if any(x in text for x in ["قهوة", "coffee", "نسكافيه", "اسبريسو"]): url = ANIMATIONS["coffee"]
    elif any(x in text for x in ["شاي", "tea", "ينسون", "نعناع"]): url = ANIMATIONS["tea"]
    elif any(x in text for x in ["ميه", "ماء", "water"]): url = ANIMATIONS["water"]
    elif any(x in text for x in ["اكل", "غدا", "ساندوتش", "food"]): url = ANIMATIONS["food"]
    return load_lottieurl(url)

# 3. إدارة الملفات (طلبات + مستخدمين)
def load_csv(file_path, columns):
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=columns)
    try:
        return pd.read_csv(file_path, encoding='utf-8-sig')
    except:
        return pd.DataFrame(columns=columns)

def save_csv(df, file_path):
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

def register_user(name, job, gender):
    df = load_csv(USERS_FILE, ["Name", "Job", "Gender", "JoinDate"])
    # التأكد إن الاسم مش متكرر، لو متكرر نحدث بياناته
    if name in df["Name"].values:
        df.loc[df["Name"] == name, ["Job", "Gender"]] = [job, gender]
    else:
        new_user = pd.DataFrame([{
            "Name": name, 
            "Job": job, 
            "Gender": gender, 
            "JoinDate": time.strftime("%Y-%m-%d")
        }])
        df = pd.concat([df, new_user], ignore_index=True)
    save_csv(df, USERS_FILE)

def save_order(name, room, order):
    df = load_csv(DATA_FILE, ["Time", "Name", "Room", "Order", "Status"])
    new_order = pd.DataFrame([{
        "Time": time.strftime("%I:%M %p"),
        "Name": name,
        "Room": room,
        "Order": order,
        "Status": "Pending"
    }])
    df = pd.concat([df, new_order], ignore_index=True)
    save_csv(df, DATA_FILE)

def mark_done(index):
    df = load_csv(DATA_FILE, ["Time", "Name", "Room", "Order", "Status"])
    if index in df.index:
        df.at[index, "Status"] = "Done"
        save_csv(df, DATA_FILE)

# 4. الستايل (CSS)
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0b0d17, #1a1c2c); color: white; }
    .order-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 5px solid #00ffcc; direction: rtl; text-align: right;
    }
    .big-font { font-size: 22px; font-weight: bold; color: #00ffcc; }
    .small-font { font-size: 14px; color: #ccc; }
    /* تنسيق زر الدخول */
    div.stButton > button { width: 100%; background-color: #00ffcc; color: black; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. منطق البرنامج (Login vs Main App)
# ---------------------------------------------------------

# التأكد من وجود مفتاح لتخزين بيانات المستخدم في الجلسة الحالية
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

# == شاشة تسجيل الدخول ==
if st.session_state["user_info"] is None:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st_lottie(load_lottieurl(ANIMATIONS["login"]), height=200, key="login_anim")
        st.markdown("<h2 style='text-align: center;'>🔐 تسجيل دخول الموظفين</h2>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            name_in = st.text_input("الاسم بالكامل")
            job_in = st.text_input("المسمى الوظيفي (Job Title)")
            # الخيارات اللي طلبتها بالظبط
            gender_in = st.selectbox("النوع / الفئة", ["ذكر", "أنثى", "مهندس"])
            
            submit_login = st.form_submit_button("دخول للنظام 🚀")
            
            if submit_login:
                if name_in and job_in:
                    # حفظ البيانات في ملف المستخدمين
                    register_user(name_in, job_in, gender_in)
                    # حفظ البيانات في الجلسة الحالية عشان يفضل فاكره
                    st.session_state["user_info"] = {
                        "name": name_in,
                        "job": job_in,
                        "gender": gender_in
                    }
                    st.success(f"أهلاً يا {name_in}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("دخل بياناتك كاملة يا هندسة!")

# == التطبيق الرئيسي (بعد الدخول) ==
else:
    # استرجاع بيانات المستخدم المسجل
    user = st.session_state["user_info"]
    
    # القائمة الجانبية
    with st.sidebar:
        st.markdown(f"### 👤 {user['name']}")
        st.caption(f"💼 {user['job']} | {user['gender']}")
        
        if st.button("تسجيل خروج 🚪"):
            st.session_state["user_info"] = None
            st.rerun()
            
        st.markdown("---")
        st.markdown("### 📥 طلب جديد")
        with st.form("order_form", clear_on_submit=True):
            # الاسم بيتاخد أوتوماتيك
            st.text_input("الاسم", value=user['name'], disabled=True)
            u_room = st.selectbox("المكان", ["المكتب الرئيسي", "غرفة الاجتماعات", "المكتب الجانبي", "الاستقبال"])
            u_order = st.text_input("عاوز تشرب/تاكل إيه؟")
            
            if st.form_submit_button("إرسال الطلب 🔥"):
                if u_order:
                    save_order(user['name'], u_room, u_order)
                    st.toast("تم الإرسال!")
                    time.sleep(1)
                    st.rerun()

    # واجهة عرض الطلبات
    st.title("⚡ LIVE OFFICE MONITOR")
    
    df = load_csv(DATA_FILE, ["Time", "Name", "Room", "Order", "Status"])
    pending = df[df["Status"] == "Pending"].iloc[::-1]

    if not pending.empty:
        for idx, row in pending.iterrows():
            col_content, col_btn = st.columns([5, 1])
            with col_content:
                c_anim, c_txt = st.columns([1, 4])
                with c_anim:
                    anim = get_anim_by_order(row['Order'])
                    if anim: st_lottie(anim, height=80, key=f"lottie_{idx}")
                    else: st.markdown("## ☕")
                with c_txt:
                    st.markdown(f"""
                    <div class="order-card">
                        <div class="big-font">{row['Order']}</div>
                        <div class="small-font">👤 {row['Name']} | 📍 {row['Room']}</div>
                        <div style="color:gray; font-size:12px;">🕒 {row['Time']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            with col_btn:
                st.write("")
                if st.button("✅ تم", key=f"done_{idx}", use_container_width=True):
                    mark_done(idx)
                    st.rerun()
    else:
        st.info("مفيش طلبات حالياً.. الهدوء يعم المكان 🍃")
    
    # التحديث التلقائي
    time.sleep(15)
    st.rerun()
