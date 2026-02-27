import streamlit as st
import google.generativeai as genai

# --- 1. ตั้งค่าหน้าเว็บ (Configuration) ---
st.set_page_config(
    page_title="SRT Creator Pro", 
    page_icon="🎙️", 
    layout="centered"
)

# Custom CSS เพื่อความสวยงาม
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .main-title {
        text-align: center;
        color: #1E88E5;
    }
    .footer {
        text-align: center;
        color: #888;
        padding: 20px;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ส่วนหัวข้อเว็บไซต์ ---
st.markdown("<h1 class='main-title'>🎵 SRT Creator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Develop by K.Anuwat</p>", unsafe_allow_html=True)
st.divider()

# --- 3. การจัดการ API Key ---
if "GEMINI_API_KEY" in st.secrets:
    api_key_input = st.secrets["GEMINI_API_KEY"]
else:
    api_key_input = st.sidebar.text_input("🔑 ใส่ Gemini API Key:", type="password")
    st.sidebar.info("แนะนำ: นำ API Key จาก Google AI Studio มาใส่ที่นี่")

# --- 4. ส่วนรับข้อมูลจาก User ---
with st.container():
    st.subheader("📂 1. อัปโหลดและตั้งค่า")
    uploaded_file = st.file_uploader("เลือกไฟล์เพลง (.mp3)", type=["mp3"])
    
    offset = st.number_input(
        "⏳ ช่วงต้นเพลงที่ไม่มีเสียงร้อง (วินาที):", 
        min_value=0.0, 
        value=0.0, 
        step=0.1
    )

    st.subheader("📝 2. เนื้อเพลง (Lyrics)")
    lyrics = st.text_area(
        "วางเนื้อเพลงที่นี่ (แยก 1 ประโยคต่อ 1 บรรทัด)", 
        placeholder="วางเนื้อเพลงที่นี่...",
        height=250
    )

# --- 5. ส่วนประมวลผล (Processing) ---
if st.button("🚀 เริ่มสร้างไฟล์ SRT (Process)"):
    if not api_key_input:
        st.error("❌ กรุณาใส่ Gemini API Key ก่อน")
    elif not uploaded_file or not lyrics:
        st.warning("⚠️ กรุณาอัปโหลดไฟล์เพลงและใส่เนื้อเพลง")
    else:
        try:
            with st.spinner('🤖 AI กำลังประมวลผล...'):
                # ตั้งค่า Gemini
                genai.configure(api_key=api_key_input)
                
                # --- จุดที่แก้ไข: ใช้ชื่อโมเดลแบบเต็มเพื่อเลี่ยง Error 404 ---
                # ลองใช้ gemini-1.5-flash ตัวมาตรฐาน
                model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
                
                prompt = f"""
                Create a standard .srt subtitle file from these lyrics:
                {lyrics}
                
                Conditions:
                1. Start the first line at {offset} seconds.
                2. Use 'Force Align' technique: One line of lyrics per one SRT block.
                3. Maintain strictly the SRT format (index, timestamp, text).
                4. Output only the SRT code.
                """
                
                response = model.generate_content(prompt)
                
                if response.text:
                    srt_output = response.text
                    clean_srt = srt_output.replace("```srt", "").replace("```", "").strip()

                    st.success("✅ สำเร็จ!")
                    st.subheader("📄 Preview SRT")
                    st.text_area("ผลลัพธ์:", value=clean_srt, height=200)
                    
                    st.download_button(
                        label="📥 ดาวน์โหลดไฟล์ .srt",
                        data=clean_srt,
                        file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}.srt",
                        mime="text/plain"
                    )
                else:
                    st.error("AI ไม่สามารถส่งข้อมูลกลับมาได้ กรุณาลองอีกครั้ง")

        except Exception as e:
            # หากยัง Error 404 ให้ลองสลับไปใช้ gemini-pro เป็นแผนสำรอง
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")
            st.info("คำแนะนำ: ตรวจสอบว่า API Key ถูกต้องและรองรับ Gemini 1.5 หรือไม่")

# --- 6. ส่วนท้าย (Footer) ---
st.markdown("<div class='footer'>SRT Creator Tool v2.2 | Develop by K.Anuwat</div>", unsafe_allow_html=True)
