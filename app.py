import streamlit as st
import google.generativeai as genai

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="SRT Creator Pro", page_icon="🎙️")

# --- 2. ส่วนการจัดการ API Key (เชื่อมกับ Secrets หรือกรอกเอง) ---
if "GEMINI_API_KEY" in st.secrets:
    api_key_input = st.secrets["GEMINI_API_KEY"]
else:
    api_key_input = st.sidebar.text_input("🔑 ใส่ Gemini API Key:", type="password")

# --- 3. ส่วนแสดงผล UI ---
st.title("🎵 SRT Creator Develop by K.Anuwat")
st.write("เครื่องมือสร้างคำบรรยายเพลงอัตโนมัติ")

with st.expander("🛠️ ส่วนการตั้งค่าและอัพโหลด", expanded=True):
    uploaded_file = st.file_uploader("📂 เลือกไฟล์เพลง (.mp3)", type=["mp3"])
    offset = st.number_input("⏳ ช่วงต้นเพลงที่ไม่มีเสียงร้อง (วินาที):", min_value=0.0, value=0.0, step=0.5)

st.subheader("📝 เนื้อเพลง (Lyrics)")
lyrics = st.text_area("วางเนื้อเพลงที่นี่ (1 ประโยคต่อ 1 บรรทัด)", height=250)

# --- 4. ส่วนประมวลผล ---
if st.button("🚀 เริ่มสร้างไฟล์ SRT (Process)"):
    # เช็คชื่อตัวแปรตรงนี้ (api_key_input)
    if not api_key_input or not uploaded_file or not lyrics:
        st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน (ไฟล์, เนื้อเพลง และ API Key)")
    else:
        try:
            with st.spinner('🤖 AI กำลังประมวลผล...'):
                genai.configure(api_key=api_key_input)
                
                # model = genai.GenerativeModel('gemini-1.5-flash')
                model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
                
                # Prompt สั่งงาน AI
                prompt = f"""
                สร้างไฟล์ .srt จากเนื้อเพลงนี้: '{lyrics}' 
                โดยเริ่มนับเวลาที่วินาทีที่ {offset} 
                กฎสำคัญ: ตัดประโยคแบบบรรทัดต่อบรรทัด (Force Align)
                """
                
                response = model.generate_content(prompt)
                srt_output = response.text

                st.success("✅ ประมวลผลสำเร็จ!")
                st.text_area("Preview SRT:", value=srt_output, height=200)
                
                st.download_button(
                    label="💾 ดาวน์โหลดไฟล์ .srt",
                    data=srt_output,
                    file_name=f"{uploaded_file.name.split('.')[0]}.srt",
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")

st.markdown("---")
st.caption("SRT Creator Tool | Develop by K.Anuwat")
