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
 
PROMPT = """
Sen bir fotoğraf analiz sistemisin. Sana gönderilen fotoğrafı aşağıdaki çerçeveye göre analiz et. Emoji kullanma. Yorum katma. Kendi adına konuşma. Sadece analiz çıktısını ver. Her bölümü sırasıyla ve düzgün bir formatta sun.

---

ANALIZ FORMATI:

1. RENK ANALIZI

- Baskın renkler ve tonları
- Renk sıcaklığı (soğuk, sıcak, nötr)
- Kontrast seviyesi (düşük, orta, yüksek)
- Renklerin psikolojik karşılıkları
- Renk geçiş yapısı (yumuşak, sert, gradyan)


2. ISIK VE GOLGE

- Işık kaynağı türü (doğal, yapay) ve yönü
- Işık yoğunluğu (yumuşak, sert, dağınık)
- Gölge derinliği ve karakteri
- Işığın fotoğrafa kattığı duygusal etki
- Tahmini zaman dilimi (gündüz, gece, altın saat, mavi saat)


3. ATMOSFER

- Genel atmosfer tanımı
- Mekansal his (açık, kapalı, geniş, dar)
- Çevresel unsurlar (sis, yağmur, toz, duman varsa)
- Zaman algısı (durağan, hareketli, donmuş)
- Sessizlik veya gürültü hissi


4. DUYGUSAL ANALIZ

- Birincil duygu
- İkincil duygular
- Duygusal yoğunluk (1-10)
- Duygusal yön (pozitif, negatif, nötr, karmaşık)
- Tetikleyebileceği evrensel çağrışımlar


5. KOMPOZISYON

- Kompozisyon yapısı (simetri, asimetri, üçler kuralı, merkezi)
- Odak noktası ve görsel çekim yönü
- Derinlik katmanları (ön plan, orta plan, arka plan)
- Negatif alan kullanımı ve etkisi
- Doku ve detay yoğunluğu


6. HIKAYE

- "Fotoğrafın anlattığı hikaye (3-5 cümle)
- "Sembolik okunabilecek unsurlar
- "Çağrıştırdığı sanat akımı
- "Fotoğraf için bir başlık önerisi
- "Tek kelimelik özet

---

KURALLAR:

- "Emoji kullanma.
- "Kendi adına cümle kurma.
- "Yorum veya değerlendirme ekleme.
- "Fotoğrafın iyi veya kötü olduğuna dair ifade kullanma.
- "Kullanıcıya hitap etme.
- "Sadece analiz çıktısını ver.
- "Her bölümü numaralı sırayla sun.
- "Fotoğrafta insan varsa beden dili, yüz ifadesi ve bakış yönünü analize dahil et.
- "Fotoğrafta doğa varsa mevsim ve hava koşullarını analize dahil et.
- "Fotoğrafta yapı veya şehir varsa mimari baskı ve mekan etkileşimini analize dahil et.
- "Türkçe yaz."""
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
 
