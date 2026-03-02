import streamlit as st
import google.generativeai as genai

# --- 1. ตั้งค่าหน้าเว็บ (Configuration) ---
st.set_page_config(
    page_title="SRT Creator Pro", 
    page_icon="🎙️", 
    layout="centered"
)

# --- 2. แก้ไข CSS เพื่อแก้ปัญหาสีตัวอักษรใน Sidebar ---
st.markdown("""
    <style>
    /* บังคับสีตัวอักษรใน Sidebar ให้ชัดเจน (แก้ปัญหาสีกลืน) */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #1a1c23 !important;
    }
    
    /* ปรับแต่งปุ่มและหัวข้อหลัก */
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
    .sub-title { text-align: center; color: #666; font-size: 0.9rem; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🎙️ SRT Creator</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Develop by K.Anuwat</p>", unsafe_allow_html=True)
st.divider()

# --- 3. การจัดการ API Key ใน Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='color: #1E88E5;'>🔑 การตั้งค่า API</h2>", unsafe_allow_html=True)
    
    # เช็ค Secret
    if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"] != "":
        api_key_input = st.secrets["GEMINI_API_KEY"]
        st.success("✅ ใช้ API Key จากระบบหลังบ้านแล้ว")
    else:
        api_key_input = st.text_input("กรอก Gemini API Key:", type="password")
        
        if not api_key_input:
            # ใช้ HTML เพื่อบังคับสีข้อความในส่วนคำแนะนำ
            st.markdown("""
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; color: #856404; margin-top: 10px;">
                    <strong>⚠️ ต้องใส่ API Key ก่อนใช้งาน</strong>
                </div>
                <div style="margin-top: 20px; color: #1a1c23;">
                    <h4 style="color: #1E88E5; margin-bottom: 5px;">🚀 ยังไม่มี API Key?</h4>
                    <p style="font-size: 0.9rem;">สร้างรหัสฟรีได้ที่นี่:</p>
                    <a href="https://aistudio.google.com/app/apikey" target="_blank" 
                       style="background-color: #1E88E5; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; font-size: 0.8rem;">
                       👉 รับ API Key ที่หน้า Google AI Studio
                    </a>
                    <p style="font-size: 0.8rem; margin-top: 15px; color: #555;">
                        <b>ขั้นตอน:</b><br>
                        1. ล็อกอิน Gmail<br>
                        2. กด Create API key<br>
                        3. ก๊อปปี้รหัสมาวางในช่องด้านบน
                    </p>
                </div>
            """, unsafe_allow_html=True)

# --- 4. ส่วนรับข้อมูลหลัก ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📂 อัปโหลดไฟล์")
    uploaded_file = st.file_uploader("เลือกไฟล์เพลง (.mp3)", type=["mp3"])

with col2:
    st.subheader("⏳ ตั้งค่าเวลา")
    offset = st.number_input("เริ่มร้องวินาทีที่ (Offset):", min_value=0.0, value=0.0, step=0.1)

st.subheader("📝 เนื้อเพลง (Lyrics)")
lyrics = st.text_area("วางเนื้อเพลง (แยก 1 ประโยคต่อ 1 บรรทัด)", height=200, placeholder="ตัวอย่าง:\nบรรทัดที่ 1\nบรรทัดที่ 2")

# --- 5. ประมวลผล ---
if st.button("🚀 เริ่มสร้างไฟล์ SRT"):
    if not api_key_input:
        st.error("❌ กรุณากรอก API Key ที่ Sidebar ด้านซ้ายก่อนครับ")
    elif not uploaded_file or not lyrics:
        st.warning("⚠️ กรุณาใส่ข้อมูลให้ครบ (ไฟล์เพลงและเนื้อเพลง)")
    else:
        try:
            with st.spinner('🤖 AI กำลังคำนวณจังหวะเพลง...'):
                genai.configure(api_key=api_key_input)
                
                # ตรวจสอบโมเดล
                all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
                selected_model_name = next((t for t in target_models if t in all_models), "models/gemini-1.5-flash")

                model = genai.GenerativeModel(selected_model_name)
                prompt = f"Create a standard .srt file from these lyrics: {lyrics} starting at {offset}s. Output only SRT code."
                
                response = model.generate_content(prompt)
                
                if response.text:
                    clean_srt = response.text.replace("```srt", "").replace("```", "").strip()
                    st.success(f"✅ สำเร็จ! (Model: {selected_model_name.split('/')[-1]})")
                    st.text_area("📄 Preview:", value=clean_srt, height=200)
                    
                    st.download_button(
                        label="📥 ดาวน์โหลด .srt",
                        data=clean_srt,
                        file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.srt",
                        mime="text/plain"
                    )
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")

st.markdown("---")
st.caption("SRT Creator Tool v3.3 | Fixed Sidebar Visibility | Develop by K.Anuwat")
