
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
FALLBACK_MODEL_ID = 'gemini-3.5-flash-lite'  # โมเดลเบา เร็ว โควตาฟรีมักสูงกว่า ใช้เมื่อโมเดลหลักโดน 503/429


def ask_motar(prompt, persona, max_retries=3):
    """
    เรียก Gemini ให้วิเคราะห์ พร้อม retry เมื่อเจอ ServerError ชั่วคราว
    ถ้าโมเดลหลัก (gemini-3.5-flash) ยัง 503 อยู่ทุกครั้ง จะลอง fallback ไป gemini-2.5-flash
    """
    for model_id in (MODEL_ID, FALLBACK_MODEL_ID):
        last_error = None
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=persona,
                    ),
                )
                return response.text
            except genai_errors.ServerError as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(3 * (attempt + 1))  # รอนานขึ้นทีละรอบ: 3, 6 วิ
                    continue
            except genai_errors.ClientError as e:
                last_error = e
                err_text = str(e)
                if "429" in err_text or "RESOURCE_EXHAUSTED" in err_text:
                    # โควตาโมเดลนี้หมด -> ไปลอง fallback model แทน ไม่ต้อง retry ซ้ำโมเดลเดิม
                    break
                # ClientError อื่นๆ (api key ผิด, request ผิดรูปแบบ) -> ไม่มีประโยชน์ที่จะลองโมเดลอื่น
                raise RuntimeError(f"เรียก Gemini ไม่สำเร็จ (ClientError, model={model_id}): {e}") from e
        # โมเดลนี้ล้มเหลวครบทุก retry แล้ว ไปลองโมเดลถัดไป (ถ้ามี)

    raise RuntimeError(
        f"เรียก Gemini ไม่สำเร็จทั้ง {MODEL_ID} และ {FALLBACK_MODEL_ID} "
        f"(อาจเป็นเพราะโควตาฟรีของทั้งสองโมเดลหมดสำหรับวันนี้): {last_error}"
    )


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

