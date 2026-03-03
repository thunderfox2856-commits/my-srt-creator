import streamlit as st
import google.generativeai as genai

# --- 1. ตั้งค่าหน้าเว็บ (Configuration) ---
st.set_page_config(
    page_title="SRT Creator Pro", 
    page_icon="🎙️", 
    layout="centered"
)

# บังคับ CSS เพื่อแก้ปัญหาสีตัวอักษรและ Sidebar
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #1a1c23 !important;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        height: 3em;
        border: none;
    }
    .main-title { text-align: center; color: #1E88E5; margin-bottom: 0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🎙️ SRT Creator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Develop by K.Anuwat</p>", unsafe_allow_html=True)
st.divider()

# --- 2. การจัดการ API Key ใน Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='color: #1E88E5;'>🔑 การตั้งค่า API</h2>", unsafe_allow_html=True)
    
    if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"] != "":
        api_key_input = st.secrets["GEMINI_API_KEY"]
        st.success("✅ ใช้ API Key จากระบบหลังบ้านแล้ว")
    else:
        api_key_input = st.text_input("กรอก Gemini API Key:", type="password")
        
        if not api_key_input:
            st.markdown("""
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; color: #856404; margin-top: 10px; border: 1px solid #ffeeba;">
                    <strong>⚠️ ต้องใส่ API Key ก่อนใช้งาน</strong>
                </div>
                <div style="margin-top: 20px;">
                    <h4 style="color: #1E88E5;">🚀 ยังไม่มี API Key?</h4>
                    <a href="https://aistudio.google.com/app/apikey" target="_blank" 
                       style="background-color: #1E88E5; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 0.8rem;">
                       👉 รับ API Key ที่นี่
                    </a>
                </div>
            """, unsafe_allow_html=True)

# --- 3. ส่วนรับข้อมูลหลัก ---
col1, col2 = st.columns([1, 1])
with col1:
    uploaded_file = st.file_uploader("เลือกไฟล์เพลง (.mp3)", type=["mp3"])
with col2:
    offset = st.number_input("เริ่มร้องวินาทีที่ (Offset):", min_value=0.0, value=0.0, step=0.1)

lyrics = st.text_area("วางเนื้อเพลง (แยก 1 ประโยคต่อ 1 บรรทัด)", height=200)

# --- 4. ประมวลผลและแก้ปัญหา Model Not Found ---
if st.button("🚀 เริ่มสร้างไฟล์ SRT"):
    if not api_key_input:
        st.error("❌ กรุณากรอก API Key ก่อนครับ")
    elif not uploaded_file or not lyrics:
        st.warning("⚠️ กรุณาใส่ข้อมูลให้ครบ")
    else:
        try:
            with st.spinner('🤖 AI กำลังค้นหาโมเดลที่เหมาะสมและประมวลผล...'):
                genai.configure(api_key=api_key_input)
                
                # ค้นหาโมเดลที่มีอยู่จริงใน API Key นี้
                available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        available_models.append(m.name)
                
                # ลำดับการเลือกโมเดล (เน้นตัวที่เสถียรที่สุด)
                selected_model = None
                priority_list = [
                    'models/gemini-1.5-flash-latest', 
                    'models/gemini-1.5-flash', 
                    'models/gemini-pro'
                ]
                
                for target in priority_list:
                    if target in available_models:
                        selected_model = target
                        break
                
                # ถ้าไม่เจอในรายการ ให้เอาตัวแรกที่รองรับ generateContent
                if not selected_model and available_models:
                    selected_model = available_models[0]
                
                if not selected_model:
                    st.error("❌ ไม่พบโมเดลที่รองรับใน API Key นี้")
                    st.stop()

                model = genai.GenerativeModel(selected_model)
                prompt = f"Create a standard .srt file from these lyrics: {lyrics} starting at {offset}s. Output only SRT code."
                
                response = model.generate_content(prompt)
                
                if response.text:
                    clean_srt = response.text.replace("```srt", "").replace("```", "").strip()
                    st.success(f"✅ สำเร็จ! (ใช้โมเดล: {selected_model})")
                    st.text_area("📄 Preview:", value=clean_srt, height=200)
                    st.download_button("📥 ดาวน์โหลด .srt", data=clean_srt, file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.srt")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")

st.markdown("---")
st.caption("SRT Creator v3.4 | Model Auto-Fix | Develop by K.Anuwat")
