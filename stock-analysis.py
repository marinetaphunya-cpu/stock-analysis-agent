import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
!pip install pandas_ta  # รันคำสั่งนี้หากยังไม่ได้ติดตั้ง
import pandas_ta as ta
!pip install -q -U google-generativeai
import google.generativeai as genai

# สร้าง model+persona
genai.configure(api_key="MY_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

# กำหนดค่า persona ที่นี่ (ตัวอย่าง: "You are a financial analyst...")
persona = "You are a financial analyst providing concise stock analysis based on fundamental and technical data." # โปรดใส่คำอธิบาย persona ที่นี่

system_instruction=persona

# ย้ายส่วนนี้ไปอยู่ในลูป for เพื่อให้ ticker_symbol และ info ถูกกำหนดค่าแล้ว
# promt=f"หุ้น {ticker_symbol} มีข้อมูลคือ: {info} ช่วยวิเคราะห์หุ้น"
# response = model.generate_content(prompt)
# print(response.text)


# 1. ตั้งค่ารายชื่อหุ้นที่สนใจ
my_stocks = ["SMR", "ASTS", "IONQ", "RKLB", "CCJ", "NVDA", "TMO"]
data_list = []

# ฟังก์ชันจัดประเภทหุ้นตามค่า P/E (ใช้ f-string และรูปแบบที่กระชับขึ้น)
def check_growth(pe):
    if pe is None or pe == 0:
        return "Growth Stock (Early/No Profit)"
    return "Growth Stock (High Expectation)" if pe > 30 
    else "Value Stock (Standard)"

# 2. เริ่มดึงข้อมูลและพล็อตกราฟ + แสดงข้อมูลพื้นฐานของหุ้นทุกตัวในลูป
for ticker_symbol in my_stocks:
    print(f"\nกำลังประมวลผลหุ้น: {ticker_symbol}...")

    # ดึงข้อมูลจาก yfinance (เวอร์ชันปัจจุบันแนะนำให้สร้างออบเจกต์ Ticker ไว้ก่อน)
    stock = yf.Ticker(ticker_symbol)

    # --- ส่วนที่ 1: ดึงข้อมูลพื้นฐาน (Fundamental Data) ---
    # ดึงข้อมูล info มาเก็บไว้ในตัวแปรเดียวเพื่อลดจำนวนการ Request ไปที่เซิร์ฟเวอร์
    stock_info = stock.info
    pe_ratio = stock_info.get('trailingPE', 0)

    # วิธีส่งข้อมูลเข้าไป (ภายใน loop)
    # ใช้ stock_info แทน info, แก้ promt เป็น prompt และส่ง system_instruction
    prompt = f"หุ้น {ticker_symbol} มีข้อมูลคือ: {stock_info} ช่วยวิเคราะห์หุ้น"
    response = model.generate_content(prompt, system_instruction=system_instruction)
    print(f"การวิเคราะห์หุ้น {ticker_symbol} โดย AI:")
    print(response.text)

    data_list.append({

