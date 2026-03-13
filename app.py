
Copy

from flask import Flask, request, Response
import base64
import os
import requests
 
app = Flask(__name__)
 
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
 
# Guncel ve aktif vision modeller - openrouter/free en guvenli fallback
MODELS = [
    "openrouter/healer-alpha",                          # OpenRouter'in kendi vision modeli, aktif
    "moonshotai/kimi-vl-a3b-thinking:free",            # Vision, aktif
    "mistralai/mistral-small-3.1-24b-instruct:free",   # Vision destekli
    "meta-llama/llama-3.2-11b-vision-instruct:free",   # Llama vision
    "google/gemma-3-27b-it:free",                      # Gemma vision
    "openrouter/free",                                  # Son care: otomatik secim
]
 
PROMPT = (
    "Sen ColorMind AI adli bir Renk Duygusu Ogretmeni yapay zekasisin. "
    "Bu gorseldeki baskin renkleri analiz et. "
    "Her renk icin yuzdesini, hex kodunu ve duygusal anlamini belirle. "
    "Gorselin genel duygusal atmosferini acikla ve kullaniciya egitici bir oneri sun. "
    "Turkce yanit ver."
)
 
@app.post("/analyze")
def analyze():
    try:
        image_data = request.get_data()
        if not image_data:
            return Response("Gorsel verisi bulunamadi", status=400, mimetype="text/plain; charset=utf-8")
 
        mime = request.content_type or "image/jpeg"
        if mime == "application/octet-stream":
            mime = "image/jpeg"
 
        base64_image = base64.b64encode(image_data).decode("utf-8")
 
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
 
        last_error = ""
 
        for model in MODELS:
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            }
 
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
 
            if r.status_code == 200:
                result = r.json()["choices"][0]["message"]["content"]
                return Response(result, mimetype="text/plain; charset=utf-8")
            else:
                last_error = r.text
                continue
 
        return Response(f"Tum modeller basarisiz oldu. Son hata: {last_error}", status=500, mimetype="text/plain; charset=utf-8")
 
    except Exception as e:
        return Response(f"Hata: {e}", status=500, mimetype="text/plain; charset=utf-8")
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
