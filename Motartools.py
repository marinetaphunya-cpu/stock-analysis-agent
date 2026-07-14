# tools.py
import yfinance as yf
import pandas_ta as ta

def get_technical_indicators(ticker):
    df = yf.download(ticker, period="5y", interval="1d")
    if len(df) < 50: return "ข้อมูลไม่พอ"
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['SMA_50'] = ta.sma(df['Close'], length=50)
    latest = df.iloc[-1]
    return {"RSI": round(latest['RSI'], 2), "SMA_50": round(latest['SMA_50'], 2)}


