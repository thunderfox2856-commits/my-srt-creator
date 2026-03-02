import streamlit as st
import google.generativeai as genai

# --- 1. ตั้งค่าหน้าเว็บ (Configuration) ---
st.set_page_config(
    page_title="SRT Creator Pro", 
    page_icon="🎙️", 
    layout="centered"
)

# ตกแต่ง UI ด้วย CSS เพื่อความสวยงามและแสดงผลได้ดีทุกอุปกรณ์
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        transition: 0.3s;
        border: none;
        height: 3em;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .main-title { text-align: center; color: #1E88E5; margin-bottom: 0; }
    .sub-title { text-align: center; color: #666; font-size: 0.9rem; margin-top: 5px; }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🎵 SRT Creator</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Develop by K.Anuwat</p>", unsafe_allow_html=True)
st.divider()

# --- 2. การจัดการ API Key ใน Sidebar ---
with st.sidebar:
    st.header("🔑 การตั้งค่า API")
    
    # ตรวจสอบว่ามี Key ใน Secrets (หลังบ้าน) หรือไม่
    if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"] != "":
        api_key_input = st.secrets["GEMINI_API_KEY"]
        st.success("✅ ระบบใช้ API Key กลางเรียบร้อยแล้ว")
    else:
        api_key_input = st.text_input("กรอก Gemini API Key ของคุณ:", type="password", help="นำรหัสจาก Google AI Studio มาวางที่นี่")
        
        if not api_key_input:
            st.warning("⚠️ กรุณาใส่ API Key เพื่อเริ่มใช้งาน")
            
            # --- ส่วนลิงก์ไปหน้า Google AI Studio ตามที่คุณต้องการ ---
            st.markdown("""
                ---
                ### 🚀 ยังไม่มี API Key?
                หากคุณยังไม่มีรหัสใช้งาน สามารถกดลิงก์ด้านล่างเพื่อสร้างได้ฟรี:
                
                👉 **[คลิกที่นี่เพื่อรับ Gemini API Key](https://aistudio.google.com/app/apikey)**
                
                **ขั้นตอนการรับรหัส:**
                1. ล็อกอินด้วยบัญชี Google
                2. กดปุ่ม **Create API key**
                3. ก๊อปปี้รหัส (ที่ขึ้นต้นด้วย AIza...) มาวางในช่องด้านบน
            """)
            st.divider()

# --- 3. ส่วนรับข้อมูลหลัก (Main UI) ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📂 อัปโหลดไฟล์")
    uploaded_file = st.file_uploader("เลือกไฟล์เพลง (.mp3)", type=["mp3"])

with col2:
    st.subheader("⏳ ตั้งค่าเวลา")
    offset = st.number_input(
        "เริ่มร้องวินาทีที่ (Offset):", 
        min_value=0.0, value=0.0, step=0.1,
        help="ระบุวินาทีที่เริ่มมีเสียงร้องประโยคแรก"
    )

st.subheader("📝 เนื้อเพลง (Lyrics)")
lyrics = st.text_area(
    "วางเนื้อเพลง (แยก 1 ประโยคต่อ 1 บรรทัด)", 
    placeholder="ตัวอย่าง:\nลืมตาขึ้นมาในตอนเช้า...\nมองไปรอบตัวไม่เห็นใคร...",
    height=250
)

# --- 4. ส่วนประมวลผล (Processing) ---
if st.button("🚀 เริ่มสร้างไฟล์ SRT"):
    if not api_key_input:
        st.error("❌ ไม่พบ API Key! กรุณากรอกรหัสที่แถบด้านซ้าย (Sidebar)")
    elif not uploaded_file or not lyrics:
        st.warning("⚠️ กรุณาอัปโหลดไฟล์เพลงและระบุเนื้อเพลงให้ครบถ้วน")
    else:
        try:
            with st.spinner('🤖 AI กำลังประมวลผลและสร้างซับไตเติ้ล...'):
                # ตั้งค่าระบบ AI
                genai.configure(api_key=api_key_input)
                
                # ระบบค้นหาโมเดลที่ใช้งานได้อัตโนมัติ (Fallback System)
                try:
                    all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                except:
                    all_models = ['models/gemini-1.5-flash']

                target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
                selected_model_name = next((t for t in target_models if t in all_models), "models/gemini-1.5-flash")

                model = genai.GenerativeModel(selected_model_name)
                
                prompt = f"""
                ภารกิจ: สร้างไฟล์ .srt มาตรฐาน
                เนื้อเพลง: 
                {lyrics}
                เงื่อนไข:
                1. เริ่มต้นบรรทัดแรกที่วินาทีที่ {offset}
                2. จัดลำดับเวลาให้สัมพันธ์กับเนื้อเพลง (Force Align)
                3. ส่งกลับเฉพาะโค้ดรูปแบบไฟล์ SRT เท่านั้น
                """
                
                response = model.generate_content(prompt)
                
                if response.text:
                    # ทำความสะอาดผลลัพธ์
                    clean_srt = response.text.replace("```srt", "").replace("```", "").strip()

                    st.success(f"✅ สร้างสำเร็จ! (โมเดล: {selected_model_name.split('/')[-1]})")
                    
                    st.subheader("📄 Preview SRT")
                    st.text_area("คุณสามารถแก้ไขจังหวะเวลาได้ที่นี่:", value=clean_srt, height=200)
                    
                    # ปุ่มดาวน์โหลด
                    file_base_name = uploaded_file.name.rsplit('.', 1)[0]
                    st.download_button(
                        label="📥 ดาวน์โหลดไฟล์ .srt",
                        data=clean_srt,
                        file_name=f"{file_base_name}.srt",
                        mime="text/plain"
                    )
                else:
                    st.error("AI ไม่สามารถสร้างเนื้อหาได้ กรุณาลองตรวจสอบเนื้อเพลงอีกครั้ง")

        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                st.error("❌ API Key ถูกระงับ (Leaked) หรือไม่มีสิทธิ์เข้าถึง")
                st.info("โปรดสร้าง Key ใหม่ที่ลิงก์ใน Sidebar และห้ามโพสต์รหัสลงในที่สาธารณะ")
            else:
                st.error(f"เกิดข้อผิดพลาด: {error_msg}")

st.markdown("---")
st.caption("SRT Creator Tool v3.2 | Develop by K.Anuwat")
