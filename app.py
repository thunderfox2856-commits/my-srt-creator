import streamlit as st
import google.generativeai as genai

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="SRT Creator Pro", 
    page_icon="🎙️", 
    layout="centered"
)

# ส่วนแต่งสวยด้วย CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .main-title { text-align: center; color: #1E88E5; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🎵 SRT Creator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Develop by K.Anuwat</p>", unsafe_allow_html=True)
st.divider()

# --- 2. การจัดการ API Key ---
# ตรวจสอบว่ามี Key ใน Secrets หรือไม่ ถ้าไม่มีให้แสดงช่องกรอกใน Sidebar
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"] != "":
    api_key_input = st.secrets["GEMINI_API_KEY"]
    st.sidebar.success("✅ ใช้ API Key จากระบบหลังบ้านแล้ว")
else:
    api_key_input = st.sidebar.text_input("🔑 ใส่ Gemini API Key ของคุณ:", type="password")
    st.sidebar.warning("กรุณาใส่ API Key เพื่อใช้งาน")

# --- 3. ส่วนรับข้อมูลจากผู้ใช้ ---
with st.container():
    st.subheader("📂 1. อัปโหลดและตั้งค่า")
    uploaded_file = st.file_uploader("เลือกไฟล์เพลง (.mp3)", type=["mp3"])
    
    offset = st.number_input(
        "⏳ เริ่มร้องที่วินาทีที่ (Offset):", 
        min_value=0.0, value=0.0, step=0.1
    )

    st.subheader("📝 2. เนื้อเพลง (Lyrics)")
    lyrics = st.text_area(
        "วางเนื้อเพลงที่นี่ (แยก 1 ประโยคต่อ 1 บรรทัด)", 
        placeholder="ตัวอย่าง:\nบรรทัดที่หนึ่ง\nบรรทัดที่สอง...",
        height=200
    )

# --- 4. ส่วนประมวลผล ---
if st.button("🚀 เริ่มสร้างไฟล์ SRT"):
    if not api_key_input:
        st.error("❌ ไม่พบ API Key! กรุณากรอกที่แถบด้านซ้ายมือ (Sidebar)")
    elif not uploaded_file or not lyrics:
        st.warning("⚠️ กรุณาอัปโหลดไฟล์เพลงและใส่เนื้อเพลงให้เรียบร้อย")
    else:
        try:
            with st.spinner('🤖 AI กำลังประมวลผล...'):
                # ตั้งค่า API
                genai.configure(api_key=api_key_input)
                
                # ตรวจสอบโมเดลที่ใช้งานได้
                all_models = [m.name for m in genai.list_models()]
                
                # ลำดับความสำคัญของโมเดลที่จะใช้
                target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
                selected_model_name = ""
                
                for target in target_models:
                    if target in all_models:
                        selected_model_name = target
                        break
                
                if not selected_model_name:
                    # ถ้าหาตัวที่ระบุไม่เจอเลย ให้ลองเอาตัวแรกที่มี
                    matching = [n for n in all_models if 'generateContent' in [m.supported_generation_methods for m in genai.list_models() if m.name == n][0]]
                    if matching:
                        selected_model_name = matching[0]
                    else:
                        st.error("❌ ไม่พบโมเดลที่รองรับใน API Key นี้")
                        st.stop()

                # เริ่มสั่งงาน AI
                model = genai.GenerativeModel(selected_model_name)
                prompt = f"""
                Create a standard .srt subtitle file from these lyrics:
                {lyrics}
                
                Conditions:
                1. Start at {offset} seconds.
                2. One line of lyrics per one SRT block.
                3. STRICTLY output only the SRT code content.
                """
                
                response = model.generate_content(prompt)
                
                if response.text:
                    # ลบ tag ส่วนเกินออกถ้า AI เติมมา
                    clean_srt = response.text.replace("```srt", "").replace("```", "").strip()

                    st.success(f"✅ สำเร็จ! (ใช้โมเดล: {selected_model_name})")
                    
                    st.subheader("📄 Preview SRT")
                    st.text_area("ผลลัพธ์:", value=clean_srt, height=200)
                    
                    # ปุ่มดาวน์โหลด
                    file_name_output = f"{uploaded_file.name.rsplit('.', 1)[0]}.srt"
                    st.download_button(
                        label="📥 ดาวน์โหลดไฟล์ .srt",
                        data=clean_srt,
                        file_name=file_name_output,
                        mime="text/plain"
                    )
                else:
                    st.error("AI ประมวลผลสำเร็จแต่ไม่มีข้อความส่งกลับมา")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")
            st.info("คำแนะนำ: หากขึ้น 403 Leaked ให้สร้าง API Key ใหม่และห้ามนำไปแปะในโค้ดบน GitHub")

st.markdown("---")
st.caption("SRT Creator Tool v3.0 | Develop by K.Anuwat")
