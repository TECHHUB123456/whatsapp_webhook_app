from flask import Flask, request
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    # Optional: Print incoming data for debugging
    print("Incoming JSON:", data)

    try:
        phone_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        message_text = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    except (KeyError, IndexError):
        return "Invalid format", 400

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    folder_name = f"messages_{date_str}"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    file_path = os.path.join(folder_name, f"{date_str}.xlsx")

    data_entry = pd.DataFrame([{
        "Phone Number": phone_number,
        "Message": message_text,
        "Time": time_str
    }])

    if os.path.exists(file_path):
        existing_df = pd.read_excel(file_path)
        final_df = pd.concat([existing_df, data_entry], ignore_index=True)
    else:
        final_df = data_entry

    final_df.to_excel(file_path, index=False)

    return "Message saved", 200

if __name__ == '__main__':
    print("Webhook running on http://localhost:5000/webhook")
    app.run(port=5000, debug=True)
