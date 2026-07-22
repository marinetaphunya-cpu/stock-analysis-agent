
import datetime
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go


def _calc_rsi(close, length: int = 14) -> pd.Series:
    """คำนวณ RSI เองโดยไม่พึ่ง pandas_ta"""
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]  # กันกรณี column ซ้ำ/MultiIndex หลุดมา
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def _calc_sma(close, length: int = 50) -> pd.Series:
    """คำนวณ SMA เองโดยไม่พึ่ง pandas_ta"""
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]  # กันกรณี column ซ้ำ/MultiIndex หลุดมา
    return close.rolling(window=length).mean()


def get_stock_price(ticker: str) -> str:
    """
    ดึงราคาหุ้นล่าสุดจากตลาดหุ้นอเมริกาโดยระบุชื่อย่อหุ้นแบบ real-time พร้อมเช็ควันหยุด
    รายละเอียดเพิ่มเติม (ถ้ามี): อาจจะมีชื่อย่อหุ้นที่คล้ายกันเช็คดูให้ดีๆ ก่อนดึงมา

    Args:
        ticker(str): ชื่อย่อหุ้นที่ต้องการ (เช่น 'asts', 'rklb')

    Returns:
        str: ราคาของหุ้นล่าสุดพร้อมวันที่ หรือข้อความแจ้งเตือนถ้าไม่มีข้อมูล
    """
    if datetime.datetime.today().weekday() >= 5:
        return "ตลาดหุ้นปิดทำการเนื่องจากเป็นวันหยุดสุดสัปดาห์"

    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    if data.empty:
        return "ไม่พบข้อมูลราคาล่าสุด"

    latest_price = data['Close'].iloc[-1]
    last_date = data.index[-1].strftime('%d-%B-%Y')
    return f"{latest_price:.2f} USD (ข้อมูลล่าสุด ณ วันที่ {last_date})"


def get_company_news(ticker: str) -> str:
    """
    ดึงข่าวหุ้นล่าสุด
    เลือกข่าวที่เกี่ยวข้องกับหุ้นนั้นและข่าวส่งผลต่อธุรกิจของหุ้นตัวนั้น

    Args:
        ticker(str): ชื่อย่อหุ้นที่ต้องการดึงข่าว (เช่น 'asts', 'rklb')

    Returns:
        str: ข้อความสรุปข่าวของหุ้นตัวนั้น (3 ข่าวล่าสุด)
    """
    stock = yf.Ticker(ticker)
    news_list = stock.news
    if not news_list:
        return "ไม่พบข่าวล่าสุดสำหรับหุ้นตัวนี้"

    news_text = "\n".join([item['title'] for item in news_list[:3]])
    return news_text


def get_stock_financials(ticker: str) -> str:
    """
    ดึงข้อมูลงบการเงินเบื้องต้น (ไตรมาสล่าสุด)
    อธิบายงบการเงินเบื้องต้นที่จำเป็นต้องรู้สำหรับนักลงทุน

    Args:
        ticker(str): ชื่อย่อหุ้นที่ต้องการดึงงบการเงิน (เช่น 'asts', 'rklb')

    Returns:
        str: สรุปงบการเงินไตรมาสล่าสุดในรูปแบบข้อความ
    """
    stock = yf.Ticker(ticker)
    financials = stock.quarterly_financials
    if financials is not None and not financials.empty:
        return financials.iloc[:, 0].to_string()  # ดึงไตรมาสล่าสุด
    return "ไม่พบข้อมูลทางการเงินล่าสุด"


def get_comprehensive_financials(ticker: str) -> str:
    """
    ดึงข้อมูลการเงินแบบครบจบ (งบกำไรขาดทุน + งบดุล ไตรมาสล่าสุด)

    Args:
        ticker(str): ชื่อย่อหุ้นที่ต้องการดึงข้อมูลการเงิน (เช่น 'asts', 'rklb')

    Returns:
        str: สรุปงบการเงินและงบดุลไตรมาสล่าสุดรวมกันในรูปแบบข้อความ
    """
    stock = yf.Ticker(ticker)
    financials = stock.quarterly_financials
    balance = stock.quarterly_balance_sheet

    if financials is None or financials.empty or balance is None or balance.empty:
        return "ไม่พบข้อมูลทางการเงินล่าสุด"

    summary = (
        f"Financials:\n{financials.iloc[:, 0].to_string()}\n\n"
        f"Balance Sheet:\n{balance.iloc[:, 0].to_string()}"
    )
    return summary


def get_technical_indicators(ticker: str):
    """
    ใช้สำหรับดึงข้อมูลและดูจังหวะเข้าซื้อ (RSI, Moving Average)

    Args:
        ticker(str): ชื่อย่อหุ้นที่ต้องการ (เช่น 'asts', 'rklb', 'mu')

    Returns:
        dict: ค่า RSI, SMA 50 วัน และราคาปิดล่าสุด
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period="5y", interval="1d", auto_adjust=True)

    if df.empty or len(df) < 50:
        return "ข้อมูลไม่เพียงพอสำหรับคำนวณ SMA 50"

    df['RSI'] = _calc_rsi(df['Close'], length=14)
    df['SMA_50'] = _calc_sma(df['Close'], length=50)

    latest = df.iloc[-1]
    return {
        "RSI": round(float(latest['RSI']), 2),
        "SMA_50": round(float(latest['SMA_50']), 2),
        "current_close": round(float(latest['Close']), 2),
    }


def plot_stock_chart(ticker: str):
    """
    สร้างกราฟราคาหุ้นพร้อมเส้น SMA 50 วัน

    Args:
        ticker(str): ชื่อย่อหุ้นที่ต้องการ (เช่น 'asts', 'rklb', 'mu')

    Returns:
        plotly.graph_objects.Figure: กราฟราคาหุ้นพร้อมเส้น SMA 50
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period="5y", interval="1d", auto_adjust=True)

    df['SMA_50'] = _calc_sma(df['Close'], length=50)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', line=dict(color='orange')))
    fig.update_layout(title=f'Chart for {ticker}', xaxis_title='Date', yaxis_title='Price')

    return fig


def get_peer_analysis(ticker: str) -> str:
    """
    ใช้เมื่อต้องการเปรียบเทียบหุ้นตัวนี้กับคู่แข่งในกลุ่มอุตสาหกรรมเดียวกัน

    Args:
        ticker(str): ชื่อย่อหุ้นที่ต้องการ (เช่น 'asts', 'rklb', 'mu')

    Returns:
        str: ข้อมูลสรุปเปรียบเทียบกับคู่แข่งในรูปแบบข้อความ
    """
    stock = yf.Ticker(ticker)
    industry = stock.info.get('industry', 'unknown')
    return f"กำลังวิเคราะห์คู่แข่งของ {ticker} ในกลุ่ม {industry}"
