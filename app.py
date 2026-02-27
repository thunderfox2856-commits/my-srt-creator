%%writefile app.py
import streamlit as st
import google.generativeai as genai
import time

# --- การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="SRT Creator Pro", page_icon="🎙️")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; background-color: #4CAF50; color: white; }
    .title-text { color: #1E88E5; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎵 SRT Creator Develop by K.Anuwat")

# --- ส่วนรับข้อมูล ---
with st.container():
    st.subheader("📂 1. อัพโหลดไฟล์และตั้งค่า")
    uploaded_file = st.file_uploader("เลือกไฟล์เพลง (.mp3)", type=["mp3"])
    
    offset = st.number_input("⏳ ช่วงต้นเพลงที่ไม่มีเสียงร้อง (วินาที):", min_value=0.0, value=0.0, step=0.5)

st.subheader("📝 2. เนื้อเพลง (Lyrics)")
lyrics = st.text_area("วางเนื้อเพลงที่นี่ (1 ประโยคต่อ 1 บรรทัด)", placeholder="เนื้อเพลง...", height=200)

# api_key = st.text_input("🔑 ใส่ Gemini API Key ของคุณ:", type="password")

# --- ส่วนการจัดการ API Key ---
# พยายามดึงจาก Secrets ของ Streamlit ก่อน (เพื่อความสะดวกและปลอดภัย)
if "GEMINI_API_KEY" in st.secrets:
    api_key_input = st.secrets["AIzaSyC06devZVJXUevUcRTL5B-wDMLxALR2jHk"]
else:
    # ถ้าไม่มีใน Secrets ให้แสดงช่องกรอกในหน้าเว็บตามปกติ
    api_key_input = st.text_input("🔑 ใส่ Gemini API Key ของคุณ:", type="password", help="นำรหัสจาก Google AI Studio มาวางที่นี่")


# --- ส่วนประมวลผล ---
if st.button("🚀 เริ่มสร้างไฟล์ SRT (Process)"):
    if not api_key or not uploaded_file or not lyrics:
        st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน (ไฟล์, เนื้อเพลง และ API Key)")
    else:
        try:
            with st.spinner('🤖 AI กำลังประมวลผลแบบ Force Align...'):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # ส่ง Prompt สั่งงาน AI
                prompt = f"สร้างไฟล์ .srt จากเนื้อเพลงนี้: '{lyrics}' โดยเริ่มจับเสียงหลังวินาทีที่ {offset} ให้ตัดคำแบบ 1 บรรทัดต่อ 1 block"
                
                # (หมายเหตุ: ใน Colab การส่งไฟล์ Audio จริงต้องใช้คำสั่ง genai.upload_file)
                # สำหรับการทดสอบเบื้องต้น AI จะสร้างโครงสร้างจากเนื้อเพลงให้ก่อน
                response = model.generate_content(prompt)
                srt_output = response.text

                st.success("✅ ประมวลผลสำเร็จ!")
                st.text_area("Preview SRT:", value=srt_output, height=200)
                
                st.download_button(
                    label="💾 ดาวน์โหลดไฟล์ .srt",
                    data=srt_output,
                    file_name="lyrics_sub.srt",
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")
