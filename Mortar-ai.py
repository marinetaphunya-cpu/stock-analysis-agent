
import streamlit as st
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from persona import my_persona
from tools import get_technical_indicators # ใส่ชื่อฟังก์ชันที่เหลือเพิ่มเข้าไปได้เลย

load_dotenv()
client = genai.Client(api_key=os.getenv('MY_API_KEY'))
MODEL_ID = 'models/gemini-3.5-flash'

def ask_motar(prompt, tools_list, persona):
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=persona,
            tools=tools_list
        )
    )
    return response.text

# --- หน้าจอแสดงผล Streamlit ---
st.title("🩺 วิเคราะห์การลงทุนกับหมอต้า")
ticker = st.text_input("ชื่อหุ้น (เช่น RKLB):", "RKLB").upper()

if st.button("วิเคราะห์"):
    tech_data = get_technical_indicators(ticker)
    prompt = f"วิเคราะห์หุ้น {ticker} ข้อมูลเทคนิค: {tech_data}"
    
    # ส่งเข้าสมองหมอต้า
    with st.spinner('หมอต้ากำลังประมวลผล...'):
        result = ask_motar(prompt, [get_technical_indicators], my_persona)
        st.write(result)
