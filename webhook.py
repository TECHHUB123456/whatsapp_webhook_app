from flask import Flask, request
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = "my_custom_token"  # ✅ set this same in Meta

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("✅ Webhook verified successfully!")
            return challenge, 200
        else:
            print("❌ Verification failed.")
            return "Verification failed", 403

    if request.method == 'POST':
        data = request.get_json()
        print("📩 Incoming message:", data)

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

@app.route("/", methods=["GET"])
def home():
    return "Webhook is running", 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
