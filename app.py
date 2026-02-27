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

# --- 3. การจัดการ API Key (ดึงจาก Secrets หรือ Sidebar) ---
if "GEMINI_API_KEY" in st.secrets:
    api_key_input = st.secrets["GEMINI_API_KEY"]
else:
    api_key_input = st.sidebar.text_input("🔑 ใส่ Gemini API Key:", type="password", help="รับรหัสได้ที่ Google AI Studio")
    st.sidebar.info("แนะนำ: ตั้งค่า API Key ใน Streamlit Secrets เพื่อความสะดวก")

# --- 4. ส่วนรับข้อมูลจาก User ---
with st.container():
    st.subheader("📂 1. อัปโหลดและตั้งค่า")
    uploaded_file = st.file_uploader("เลือกไฟล์เพลง (.mp3)", type=["mp3"])
    
    offset = st.number_input(
        "⏳ ช่วงต้นเพลงที่ไม่มีเสียงร้อง (กี่วินาที):", 
        min_value=0.0, 
        value=0.0, 
        step=0.1,
        help="ใส่จำนวนวินาทีก่อนที่เนื้อร้องประโยคแรกจะเริ่ม"
    )

    st.subheader("📝 2. เนื้อเพลง (Lyrics)")
    lyrics = st.text_area(
        "วางเนื้อเพลงที่นี่ (แยก 1 ประโยคต่อ 1 บรรทัด)", 
        placeholder="เช่น:\nลืมตาขึ้นมาในตอนเช้า...\nมองไปรอบตัวไม่เห็นใคร...",
        height=250
    )

# --- 5. ส่วนประมวลผล (Processing) ---
if st.button("🚀 เริ่มสร้างไฟล์ SRT (Process)"):
    if not api_key_input:
        st.error("❌ กรุณาใส่ Gemini API Key ก่อนดำเนินการ")
    elif not uploaded_file or not lyrics:
        st.warning("⚠️ กรุณาอัปโหลดไฟล์เพลงและใส่เนื้อเพลงให้ครบถ้วน")
    else:
        try:
            with st.spinner('🤖 AI กำลังประมวลผลและจัดจังหวะเพลง (Force Align)...'):
                # ตั้งค่า Gemini
                genai.configure(api_key=api_key_input)
                
                # ใช้โมเดลเวอร์ชันล่าสุดที่เสถียร
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # สร้างข้อความสั่งงาน (Prompt)
                prompt = f"""
                ภารกิจ: สร้างไฟล์คำบรรยาย (.srt) มาตรฐาน
                เนื้อเพลงที่ให้มา: 
                {lyrics}
                
                เงื่อนไข:
                1. เริ่มคำแรกที่วินาทีที่ {offset}
                2. ใช้เทคนิค Force Align: 1 บรรทัดเนื้อเพลง = 1 ลำดับในไฟล์ SRT
                3. ห้ามข้ามเนื้อเพลง และห้ามสรุปเนื้อหา
                4. ให้ส่งกลับมาเฉพาะโค้ดในรูปแบบไฟล์ .srt เท่านั้น
                """
                
                # เรียกใช้งาน AI
                response = model.generate_content(prompt)
                srt_output = response.text

                # ลบเครื่องหมาย ```srt หรือ ``` ที่ AI อาจจะเติมมาออก
                clean_srt = srt_output.replace("```srt", "").replace("```", "").strip()

                st.success("✅ สร้างไฟล์ SRT สำเร็จ!")
                
                # แสดงผลลัพธ์
                st.subheader("📄 Preview SRT Content")
                st.text_area("สามารถแก้ไขเพิ่มเติมได้ที่นี่:", value=clean_srt, height=200)
                
                # ปุ่มดาวน์โหลด
                file_name_output = f"{uploaded_file.name.rsplit('.', 1)[0]}.srt"
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์ .srt ไปใช้งาน",
                    data=clean_srt,
                    file_name=file_name_output,
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ AI: {str(e)}")

# --- 6. ส่วนท้าย (Footer) ---
st.markdown("<div class='footer'>SRT Creator Tool v2.1 | Powered by Gemini 1.5 Flash<br>© 2026 Develop by K.Anuwat</div>", unsafe_allow_html=True)
