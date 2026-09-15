import os
import uuid
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешает веб-сайту делать запросы к серверу

# Твой авторизационный ключ GigaChat (укажи его тут или в Variables на Railway)
GIGACHAT_AUTH_KEY = os.environ.get("GIGACHAT_AUTH_KEY" "01a09488-7020-70be-a981-c8655706bb5d")

access_token = None

def get_gigachat_token():
    global access_token
    token_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {GIGACHAT_AUTH_KEY}"
    }
    payload = "scope=GIGACHAT_API_PERS"
    
    # Отключаем проверку SSL-сертификата Сбера (verify=False)
    response = requests.post(token_url, headers=headers, data=payload, verify=False)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        raise Exception(f"Ошибка получения токена: {response.text}")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        messages = data.get("messages", [])
        
        token = get_gigachat_token()
        api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        payload = {
            "model": "GigaChat",
            "messages": messages,
            "temperature": 0.7
        }
        
        response = requests.post(api_url, headers=headers, json=payload, verify=False)
        if response.status_code == 200:
            result = response.json()
            ai_text = result["choices"][0]["message"]["content"]
            return jsonify({"success": True, "reply": ai_text})
        else:
            return jsonify({"success": False, "error": response.text}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    # Запуск сервера
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
