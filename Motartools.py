
import yfinance as yf
#import pandas_ta as ta

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
    #df['RSI'] = ta.rsi(df['Close'], length=14)
    # คำนวณ SMA 50 วัน
    #df['SMA_50'] = ta.sma(df['Close'], length=50)

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
    #df['RSI'] = ta.rsi(df['Close'], length=14)
    #df['SMA_50'] = ta.sma(df['Close'], length=50)

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


