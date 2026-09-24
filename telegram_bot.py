import requests

def send_telegram_alert(bot_token, chat_id, message_text, pdf_bytes=None):
    """
    ផ្ញើសារសង្ខេប និង File PDF របាយការណ៍ទៅកាន់ Telegram
    """
    # 1. ផ្ញើសារអត្ថបទ (Text Message)
    url_msg = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message_text, "parse_mode": "HTML"}
    response = requests.post(url_msg, data=payload)
    
    # 2. ផ្ញើ File PDF (ប្រសិនបើមាន)
    if pdf_bytes is not None:
        url_doc = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        files = {'document': ('Executive_Revenue_Forecast.pdf', pdf_bytes, 'application/pdf')}
        data = {'chat_id': chat_id, 'caption': '📄 របាយការណ៍ព្យាករណ៍ចំណូលថវិការដ្ឋ (Executive PDF Report)'}
        requests.post(url_doc, data=data, files=files)
        
    return response.status_code == 200