# ==========================================================
# 1. SETUP: ส่วนติดตั้งและนำเข้าเครื่องมือ
# ==========================================================
!pip install -q -U google-genai yfinance
!pip install yfinance pandas pandas_ta
!pip install yfinance --
!pip install python-dotenv
import yfinance as yf
from google import genai
from google.colab import userdata
import datetime
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
import streamlit as st

# โหลดค่าจากไฟล์ .env เข้ามาในระบบ
load_dotenv()

# ดึงค่าออกมาใช้
api_key = os.getenv('MY_API_KEY')


# ==========================================================
# 2. CONNECTION: ส่วนการเชื่อมต่อกับสมอง AI
# ==========================================================
client client = genai.Client(api_key=api_key)
# ==========================================================
# เครื่องมือ Tools
def get_stock_price(ticker: str) -> float:
  """
   ดึงราคาหุ้นล่าสุดจากตลาดหุ้นอเมริกาโดยระบุชื่อย่อหุ้นแบบ real-time พร้อมเช็ควันหยุด
  รายละเอียดเพิ่มเติม (ถ้ามี): อาจจะมีชื่อย่อหุ้นที่คล้ายกันเช็คดูให้ดีๆ ก่อนดึงมา
  Args:
        ticker(str): ชื่อย่อหุ้นที่ต้องการ (เช่น 'asts', 'rklb')

  Returns:
        float: ราคาของหุ้นล่าสุดหน่วยเป็นดอลล่าและบาท
  """
  if datetime.datetime.today().weekday() >= 5:
    return "ตลอดหุ้นปิดทำการเนื่องจากเป็นวันหยุดสุดสัปดาห์"
  stock = yf.Ticker(ticker)
  data = stock.history(period="1d")
  if data.empty:
    return "ไม่พบข้อมูลราคาล่าสุด"
  lastest_price = data['Close'].iloc[-1]
  last_date = data.index[-1].strftime('%d-%B-%Y')
  return f"{lastest_price: .2f} USD(ข้อมูลล่าสุด ณ วันที่ {last_date})"

  # ดึงข้อมูลแบบเร็วมาก fast
  # fast_info = stock.fast_info
  #if not fast_info.get('last_price'):
    #return 0.0
  #price = stock.fast_info.get['last_price']
  #if not price:
    #return "ไม่พบข้อมูลราคา (เนื่องจากไม่มีการซื้อขายหุ้นหรือตลาดปิด)"

  #return float(price)

def get_company_news(ticker: str):
 """
  ดึงข่าวหุ้นล่าสุด
  เลือกข่าวที่เกี่ยวข้องกับหุ้นนั้นและข่าวส่งผลต่อธุรกิจของหุ้นตัวนั้น
  Args:
        ticker(str): ข่าวหุ้นที่ต้องการ (เช่น 'การขึ้นดอกเบี้ยของธนาคารกลางสหรัฐหรือเฟด', 'ราคาทองและนำมันที่ปรับตัวจากสงคราม, 'การเพิ่มฐานการผลิต')
  Returns:
        str: ข้อความสรุปข่าวของหุ้นตัวนั้น
  """
 stock = yf.Ticker(ticker)
 news_list = stock.news
# รวมข่าว 3 ข่าว
 news_text  = "\n".join([item['title'] for item in news_list[:3]])
 return news_text

def get_stock_financials(ticker: str):
  """ ดึงข้อมูลงบการเงินเบื้องต้น
  อธิบายงบการเงินเบื้องต้นที่จำเป็นต้องรู้สำหรับนักลงทุน"""
  stock = yf.Ticker(ticker)
  financials = stock.quarterly_financials
  if financials is not None and not financials.empty:
    return financials.iloc[:, 0].to_string() # ดึงไตรมาสล่าสุด
  return "ไม่พบข้อมูลทางการเงินล่าสุด"

def get_comprehensive_financials(ticker:str):
    """ ถ้าต้องการดึงข้อมูลการเงินแบบครบจบ """
    stock = yf.Ticker(ticker)
    financials = stock.quarterly_financials
    balance = stock.quarterly_balance_sheet
    # รวมข้อมูลเป็น string สั้นๆ เพื่อให้เอไอวิเคราะห์
    summary = f"Financials: {financials.iloc[:, 0].to_string()} \n Balance Sheet: {balance.iloc[:, 0].to_string()}"
    return summary


# ฟังก์ชันวิเคราะห์ทางเทคนิค (Technical Indicators)
def get_technical_indicators(ticker: str):
    """ใช้สำหรับดึงข้อมูลและดูจังหวะเข้าซื้อ (RSI, Moving Average)
    Args:
        ticker(str): ชื่อย่อหุ้นที่ต้องการ (เช่น 'asts', 'rklb', 'mu')

    # Returns:
       # float: ราคาของหุ้นล่าสุดหน่วยเป็นดอลล่าและบาท

    """
    df = yf.download(ticker, period="5y", interval="1d")
    # เช็คข้อมูลว่ามาไหม
    if len(df) < 50:
        return "ข้อมูลไม่เพียงพอสำหรับคำนวณ sma 50"
    # คำนวณ RSI
    df['RSI'] = ta.rsi(df['Close'], length=14)
    # คำนวณ SMA 50 วัน
    df['SMA_50'] = ta.sma(df['Close'], length=50)

    latest = df.iloc[-1]
    return {
        "RSI": round(latest['RSI'], 2),
        "SMA_50": round(latest['SMA_50'], 2),
        "current_close": round(float(latest['Close']), 2)

    }


def plot_stock_chart(ticker):
    # ดึงข้อมูลใหม่
    df = yf.download(ticker, period="5y", interval="1d")

    # คำนวณ RSI และ SMA50 เหมือนเดิม
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['SMA_50'] = ta.sma(df['Close'], length=50)

    # สร้างกราฟ
    fig = go.Figure()

    # เพิ่มเส้นราคา
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='blue')))

    # เพิ่มเส้น SMA 50
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', line=dict(color='orange')))

    fig.update_layout(title=f'Chart for {ticker}', xaxis_title='Date', yaxis_title='Price')
    return fig




# ฟังก์ชันเปรียบเทียบหุ้นในกลุ่ม (Peer Comparison - ตัวอย่าง)
def get_peer_analysis(ticker: str) -> str:
    """ใช้เมื่อต้องการเปรียบเทียบหุ้นตัวนี้กับคู่แข่ง
    Args:
    ticker(str): ชื่อย่อหุ้นที่ต้องการ (เช่น 'asts', 'rklb', 'mu')

   Returns:
   ข้อมูลสรุปเปรียบเทียบกับคู่แข่งในรูปแบบข้อความ
   """
  # ตัวอย่าง: ดึงข้อมูลคู่แข่งจาก info แล้วสรุปสั้นๆ
    stock = yf.Ticker(ticker)
    Industry = stock.info.get('industry', 'unknown')
    return f"กำลังวิเคราะห์คู่แข่งของ {ticker} ในกลุ่ม {stock.info.get('industry')}"


# ==========================================================
# 3. PERSONA (ใหม่!): ส่วนกำหนดบุคลิกและบทบาทของ AI
# ตรงนี้คือ 'Persona' ที่ไอด้าถามหาเจ้า เรากำหนดให้เขาเป็นนักวิเคราะห์มืออาชีพ
# ==========================================================
my_persona = """
เฮ้ หมอต้า! หมอเป็นผู้ชายและคือนักวิเคราะห์หุ้นมืออาชีพของไอด้านะ ให้เรียกแทนตัวเองว่าผม หมอต้าคือนักวางแผนเชิงกลยุทธ์ ช่วยวิเคราะห์ปัจจัยพื้นฐานของหุ้น
จากงบการเงินล่าสุดที่มี แล้วบอกไอด้าหน่อยว่าหุ้นตัวนี้อยู่ในวัฆฏจักรของธุรกิจในช่วงไหน และก่อนจะตอบคำถามช่วยบอกก่อนว่าใช้เครื่องมือ Tool ตัวไหนในการหาคำตอบ
แล้วช่วยแสดงขั้นตอนการดึงข้อมูลจากเครื่องออกมาให้ดูด้วย
กฎการทำงาน:
1. เมื่อไอด้าถามหาราคา ให้หมอต้าตรวจสอบข้อมูลจากทุกเครื่องมือที่มี
2. กฎสำคัญที่สุด: ห้ามใช้ข้อมูลจากเครื่องมือใดก็ตามที่ให้ข้อมูลเก่าเกิน 7 วัน (อดีตปี 2024 หรือ 2025 ให้ถือว่าใช้ไม่ได้)
3. หาก get_stock_price ให้ข้อมูลเก่า ให้ละทิ้งข้อมูลนั้นทันที และใช้เครื่องมือ google เพื่อค้นหาข้อมูลปัจจุบัน (ปี 2026) เท่านั้น
4. หากคุณหาข้อมูลปัจจุบันจาก google ไม่เจอจริงๆ ให้ตอบว่า ' ไม่พบราคาปัจจุบันจากตลาดหุ้น' (อนุญาตให้ใช้คำตอบนี้ ถ้าหาไม่เจอจริงๆ)
5. ห้ามเดาตัวเลขและห้ามเอาข้อมูลปี 2024 มาตอบเป็นอันขาด เข้าใจไหมคะ หมอต้า ><
6. เชื่อมโยงข่าว งบการเงิน พื้นฐานของบริษัทนั้นและความต้องการในอนาคต
7.ตอนนี้หมอต้ามีข้อมูลจากนักวิเคราะห์และข้อมูลทาง technical ใช้วิเคราะห์ volume เวลามีกองทุนใหญ่หรือเจ้ามือกำลังทยอยซื้อเพื่อช่วยแนะนำสิ่งที่เป็นประโยชน์กับไอด้า

"""

# เปลี่ยนไปใช้โมเดลอื่น เช่น 'gemini-3.1'
model_id = 'models/gemini-3.5-flash'

# ==========================================================
# 4. INPUT & DATA: ส่วนรับคำสั่งและดึงข้อมูล
# ==========================================================
ticker = input("ระบุชื่อหุ้น: ").upper()
question = input("อยากรู้อะไร?: ")
stock = yf.Ticker(ticker).info
prompt = f"หุ้น {ticker} ข้อมูลเบื้องต้น: P/E={stock.get('trailingPE')}, Sector={stock.get('sector')}. คำถาม: {question}"
# เช็ค debug
print(f"('รายละเอียดเพิ่มเติมเกี่ยวกับธุรกิจ'): ข้อมูลที่ดึงได้-P/E: {stock.get('trailingPE')}, Sector: {stock.get('sector')}")

# ส่วนเครื่องมือ
tools = [get_stock_price, get_company_news, get_stock_financials, get_comprehensive_financials, get_technical_indicators, get_peer_analysis]
# ==========================================================
# 5. GENERATION: ส่วนส่งคำสั่งพร้อมใส่ Persona
# เราเอา my_persona มาใส่ใน config เพื่อคุมพฤติกรรมเอเจ้นท์
# ==========================================================
response = client.models.generate_content(
    model=model_id,
    contents=prompt,
    config=genai.types.GenerateContentConfig(
        system_instruction=my_persona,
        tools=tools
    )
)

# ==========================================================
# 6. OUTPUT: ส่วนแสดงผลลัพธ์
# ==========================================================
print("\n--- ผลการวิเคราะห์จากนักวิเคราะห์ส่วนตัวของไอด้า ---")
print(response.text)
