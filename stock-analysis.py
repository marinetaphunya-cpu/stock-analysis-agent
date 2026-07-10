import yfinance as yf
import google.generativeai as genai
from google.colab import userdata

# 1. เชื่อมต่อสมอง
api_key = userdata.get('MY_API_KEY')
genai.configure(api_key=api_key)

# 2. ตั้ง Persona (System Instruction)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="""คุณคือนักวิเคราะห์การเงินมืออาชีพ 
    จงวิเคราะห์ข้อมูลหุ้นด้วยความแม่นยำ มีเหตุผล และสรุปประเด็นสำคัญให้เข้าใจง่าย"""
)

# 3. รายชื่อหุ้นที่สนใจ
my_stocks = ["SMR", "ASTS", "IONQ", "RKLB", "CCJ", "NVDA", "TMO"]

# --- ส่วนสำหรับรับคำถามจากไอด้า ---
print("=== ยินดีต้อนรับสู่ระบบวิเคราะห์หุ้นอัจฉริยะ ===")
user_question = input("วันนี้อยากให้ AI วิเคราะห์หุ้นด้วยมุมมองไหนเป็นพิเศษไหม? (เช่น วิเคราะห์ความเสี่ยง, วิเคราะห์ระยะยาว, หรือเปรียบเทียบ): ")

# 4. ลูปการทำงาน
for ticker_symbol in my_stocks:
    print(f"\n--- กำลังวิเคราะห์: {ticker_symbol} ---")
    
    # ดึง Data
    stock = yf.Ticker(ticker_symbol)
    stock_info = stock.info
    
    # เตรียม Prompt แบบรวมคำสั่ง Standard + คำถามจากไอด้า
    prompt = f"""
    ช่วยวิเคราะห์หุ้น {ticker_symbol} ตามข้อมูลพื้นฐานนี้:
    - Sector: {stock_info.get('sector', 'N/A')}
    - P/E Ratio: {stock_info.get('trailingPE', 'N/A')}
    - Market Cap: {stock_info.get('marketCap', 'N/A')}
    
    คำถามพิเศษที่ผู้ใช้ต้องการทราบ: {user_question}
    
    หากไม่มีคำถามพิเศษ ให้วิเคราะห์ภาพรวมและโอกาสเติบโตให้ด้วย
    """
    
    # รัน AI
    response = model.generate_content(prompt)
    print(response.text)
    print("-" * 50)


