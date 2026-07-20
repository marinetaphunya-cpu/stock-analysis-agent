
import streamlit as st
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
import os
import time
from personatar import my_persona
from Motartools import get_technical_indicators  # ใส่ฟังก์ชันอื่นเพิ่มได้ใน list ด้านล่าง

api_key = st.secrets["MY_API_KEY"]
client = genai.Client(api_key=api_key)

MODEL_ID = 'gemini-3.5-flash'


def ask_motar(prompt, persona, max_retries=3):
    """
    เรียก Gemini ให้วิเคราะห์ พร้อม retry เมื่อเจอ ServerError ชั่วคราว
    (ไม่ส่ง tools ซ้ำ เพราะข้อมูลถูกดึงมาและใส่ใน prompt เรียบร้อยแล้ว)
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=persona,
                ),
            )
            return response.text
        except genai_errors.ServerError as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))  # รอนานขึ้นทีละรอบก่อนลองใหม่
                continue
        except genai_errors.ClientError as e:
            # request ผิดรูปแบบ / api key ผิด / เกิน quota -> ไม่ควร retry
            raise RuntimeError(f"เรียก Gemini ไม่สำเร็จ (ClientError): {e}") from e

    raise RuntimeError(f"เรียก Gemini ไม่สำเร็จหลังลอง {max_retries} ครั้ง (ServerError): {last_error}")


# --- หน้าจอแสดงผล Streamlit ---
st.title("🩺 วิเคราะห์การลงทุนกับหมอต้า💸")
ticker = st.text_input("วันนี้คุยอะไรเกี่ยวกับหุ้นดี📈📉:", "RKLB").upper()

if st.button("วิเคราะห์⌛️"):
    with st.spinner('หมอต้ากำลังวิเคราะห์อยู่...🫪'):
        try:
            tech_data = get_technical_indicators(ticker)
            prompt = f"วิเคราะห์หุ้น {ticker} ข้อมูลเทคนิค: {tech_data}"
            result = ask_motar(prompt, my_persona)
            st.write(result)
        except RuntimeError as e:
            st.error(f"เกิดข้อผิดพลาดตอนคุยกับ Gemini: {e}")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")
