from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import pandas as pd
import spacy
import langdetect

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load Excel Data
complaints_df = pd.read_excel(r"C:\Users\rahul.k\Downloads\comlpaiyts.xlsx")
billing_df = pd.read_excel(r"C:\Users\rahul.k\Downloads\master table data.xlsx")

@app.get("/", response_class=JSONResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def detect_language(text: str) -> str:
    """Detect language (English, Hindi, or Hinglish)."""
    try:
        lang = langdetect.detect(text)
        return "hi" if lang == "hi" else "en"
    except:
        return "en"

def process_query(query: str) -> str:
    """Process user queries and return appropriate responses in Hindi, English, or Hinglish."""
    lang = detect_language(query)
    doc = nlp(query.lower())

    # 🔹 Bill Inquiry
    if any(token.text in ["bill", "amount", "payment", "account", "status"] for token in doc):
        for acc in billing_df["ACCOUNT_NO"].astype(str):
            if acc in query:
                data = billing_df[billing_df["ACCOUNT_NO"].astype(str) == acc]
                if not data.empty:
                    name = data.iloc[0]["NAME"]
                    load = data.iloc[0]["CONSUMER_LOAD"]
                    meter_no = data.iloc[0]["METER_NUMBER"]
                    bill_status = data.iloc[0]["BILLING_STATUS"]
                    last_bill_month = data.iloc[0]["LAST_BILLMONTH_YEAR"]
                    bill_amt = data.iloc[0]["BILL_AMOUNT"]
                    amount_paid = data.iloc[0]["AMOUNT_PAID"]
                    office_name = data.iloc[0]["OFFICE_NAME"]

                    if lang == "hi":
                        return (f"💡 **खाते {acc} की जानकारी:**\n"
                                f"👤 नाम: {name}\n"
                                f"⚡ उपभोक्ता लोड: {load} kW\n"
                                f"🔢 मीटर नंबर: {meter_no}\n"
                                f"📜 बिलिंग स्थिति: {bill_status}\n"
                                f"🗓️ अंतिम बिल महीना: {last_bill_month}\n"
                                f"💰 बिल राशि: ₹{bill_amt}\n"
                                f"✅ भुगतान राशि: ₹{amount_paid}\n"
                                f"🏢 कार्यालय: {office_name}")

                    return (f"**Account {acc} Details:**\n"
                            f"👤 Name: {name}\n"
                            f"⚡ Consumer Load: {load} kW\n"
                            f"🔢 Meter Number: {meter_no}\n"
                            f"📜 Billing Status: {bill_status}\n"
                            f"🗓️ Last Bill Month-Year: {last_bill_month}\n"
                            f"💰 Bill Amount: ₹{bill_amt}\n"
                            f"✅ Amount Paid: ₹{amount_paid}\n"
                            f"🏢 Office: {office_name}")
        return "❌ Please provide a valid account number." if lang == "en" else "❌ कृपया एक मान्य खाता नंबर प्रदान करें।"

    # 🔹 Power Cut Information
    elif "bijli" in query and "kab" in query:
        return ("⚡ Patna me bijli 2 ghante me wapas aayegi. 📞 Call 1912 for updates." if lang == "hi"
                else "⚡ Electricity will be restored in 2 hours in Patna. Call 1912 for updates.")

    # 🔹 Complaint Status
    elif any(token.text in ["complaint", "issue", "problem", "status"] for token in doc):
        for acc in complaints_df["ACCOUNT_NO"].astype(str):
            if acc in query:
                data = complaints_df[complaints_df["ACCOUNT_NO"].astype(str) == acc]
                if not data.empty:
                    request_type = data.iloc[0]["REQUEST_TYPE"]
                    status = data.iloc[0]["APP_STATUS"]

                    return (f"📢 **शिकायत की स्थिति:**\n🔹 प्रकार: {request_type}\n🔹 स्थिति: {status}" if lang == "hi"
                            else f"📢 **Complaint Status:**\n🔹 Type: {request_type}\n🔹 Status: {status}")
        return "कोई शिकायत नहीं मिली।" if lang == "hi" else "No complaints found for this account."

    # 🔹 New Connection Inquiry
    elif "naya connection" in query:
        return ("✅ **नया बिजली कनेक्शन प्रक्रिया:**\n"
                "1️⃣ [SBPDCL Website](https://www.sbpdcl.co.in) पर जाएं\n"
                "2️⃣ ऑनलाइन आवेदन करें\n"
                "3️⃣ सुरक्षा जमा राशि का भुगतान करें\n"
                "4️⃣ 7 दिनों में मीटर इंस्टॉल होगा\n"
                "📞 हेल्पलाइन: 1912" if lang == "hi"
                else "✅ **New Connection Process:**\n"
                     "1️⃣ Visit: [SBPDCL Website](https://www.sbpdcl.co.in)\n"
                     "2️⃣ Apply Online\n"
                     "3️⃣ Pay Security Deposit\n"
                     "4️⃣ Meter Installation in 7 Days\n"
                     "📞 Helpline: 1912")

    # 🔹 Load Extension
    elif "load" in query and "badhana" in query:
        return ("🔹 **लोड बढ़ाने की प्रक्रिया:**\n"
                "1️⃣ [SBPDCL Website](https://www.sbpdcl.co.in) पर आवेदन करें\n"
                "2️⃣ एड्रेस और आईडी प्रूफ अपलोड करें\n"
                "3️⃣ लोड बढ़ाने की फीस जमा करें\n"
                "📞 हेल्पलाइन: 1912" if lang == "hi"
                else "🔹 **Load Enhancement Process:**\n"
                     "1️⃣ Apply Online at [SBPDCL Website](https://www.sbpdcl.co.in)\n"
                     "2️⃣ Upload Address & ID Proof\n"
                     "3️⃣ Pay Load Enhancement Fee\n"
                     "📞 Helpline: 1912")

    # 🔹 Smart Meter Benefits
    elif "smart meter" in query:
        return ("🔹 **स्मार्ट मीटर के फायदे:**\n"
                "✅ ऑनलाइन रिचार्ज\n"
                "✅ सटीक बिलिंग\n"
                "✅ तुरंत कटौती/रीकनेक्शन\n"
                "✅ मासिक उपयोग अलर्ट" if lang == "hi"
                else "🔹 **Smart Meter Benefits:**\n"
                     "✅ Online Recharge\n"
                     "✅ Accurate Billing\n"
                     "✅ Instant Power Cut/Reconnection\n"
                     "✅ Monthly Usage Alerts")

    # 🔹 Default Response
    else:
        return ("🤖 मुझे आपकी बात समझ में नहीं आई! क्या आप बिजली बिल, शिकायत या नए कनेक्शन के बारे में पूछ रहे हैं?" if lang == "hi"
                else "🤖 I didn't understand! Are you asking about your electricity bill, complaint, or new connection?")

@app.post("/chat/")
async def chat(message: str = Form(...)):
    reply = process_query(message)
    return {"reply": reply}
