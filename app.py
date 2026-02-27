import streamlit as st
import google.generativeai as genai

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="SRT Creator Pro", page_icon="🎙️")

st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🎵 SRT Creator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Develop by K.Anuwat</p>", unsafe_allow_html=True)
st.divider()

# --- 2. การจัดการ API Key ---
if "GEMINI_API_KEY" in st.secrets:
    api_key_input = st.secrets["GEMINI_API_KEY"]
else:
    api_key_input = st.sidebar.text_input("🔑 ใส่ Gemini API Key:", type="password")

# --- 3. ส่วนรับข้อมูล ---
uploaded_file = st.file_uploader("📂 เลือกไฟล์เพลง (.mp3)", type=["mp3"])
offset = st.number_input("⏳ เริ่มร้องที่วินาทีที่:", min_value=0.0, value=0.0, step=0.1)
lyrics = st.text_area("📝 วางเนื้อเพลง (1 ประโยคต่อ 1 บรรทัด)", height=200)

# --- 4. ส่วนประมวลผล (ปรับปรุงเพื่อแก้ 404) ---
if st.button("🚀 เริ่มสร้างไฟล์ SRT"):
    if not api_key_input or not uploaded_file or not lyrics:
        st.warning("กรุณากรอกข้อมูลให้ครบ")
    else:
        try:
            with st.spinner('🤖 AI กำลังประมวลผล...'):
                genai.configure(api_key=api_key_input)
                
                # --- เทคนิคใหม่: ค้นหาโมเดลที่ Key นี้มีสิทธิ์ใช้จริงๆ ---
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # เลือกโมเดลที่เหมาะสมที่สุด (ลอง Flash ก่อน ถ้าไม่มีใช้ Pro)
                selected_model = ""
                for target in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
                    if target in available_models:
                        selected_model = target
                        break
                
                if not selected_model:
                    st.error("ไม่พบโมเดลที่รองรับใน API Key นี้")
                else:
                    model = genai.GenerativeModel(selected_model)
                    prompt = f"Create SRT from these lyrics starting at {offset}s: {lyrics}. Output only SRT format."
                    
                    response = model.generate_content(prompt)
                    srt_output = response.text.replace("```srt", "").replace("```", "").strip()

                    st.success(f"สำเร็จ! (ใช้โมเดล: {selected_model})")
                    st.text_area("Preview:", value=srt_output, height=200)
                    st.download_button("📥 ดาวน์โหลด .srt", data=srt_output, file_name="output.srt")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")
            st.info("ตรวจสอบว่าคุณเปิดใช้งาน Gemini API ใน Google Cloud Project แล้วหรือยัง")

st.caption("© 2026 SRT Creator Tool | Develop by K.Anuwat")
