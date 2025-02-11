import os
import shutil
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from PIL import Image
import ffmpeg

app = FastAPI()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Converter</title>
</head>
<body>
    <h1>Multi-Converter</h1>
    <ul>
        <li><a href="/imageconverter">Image Converter</a></li>
        <li><a href="/colorpicker">Color Picker</a></li>
        <li><a href="/audioconverter">Audio Converter</a></li>
        <li><a href="/videoconverter">Video Converter</a></li>
    </ul>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

# IMAGE CONVERTER
IMG_CONVERTER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Image Converter</title>
</head>
<body>
    <h1>Convert Image</h1>
    <form id="uploadForm">
        <input type="file" id="imageUpload" required>
        <select id="format">
            <option value="png">PNG</option>
            <option value="jpg">JPG</option>
            <option value="webp">WEBP</option>
        </select>
        <button type="submit">Convert</button>
    </form>
    <script>
        document.getElementById("uploadForm").onsubmit = async function(event) {
            event.preventDefault();
            let fileInput = document.getElementById("imageUpload").files[0];
            let format = document.getElementById("format").value;
            let formData = new FormData();
            formData.append("image", fileInput);
            formData.append("format", format);
            
            let response = await fetch("/convert-image", { method: "POST", body: formData });
            let data = await response.json();
            window.location.href = data.url;
        };
    </script>
</body>
</html>
"""

@app.get("/imageconverter", response_class=HTMLResponse)
async def image_converter_page():
    return IMG_CONVERTER_HTML

@app.post("/convert-image")
async def convert_image(image: UploadFile, format: str = Form("png")):
    input_path = f"/tmp/{image.filename}"
    output_path = f"/tmp/converted.{format}"
    with open(input_path, "wb") as f:
        f.write(await image.read())
    
    img = Image.open(input_path)
    img.save(output_path, format.upper())
    
    return JSONResponse({"url": f"/download?file=converted.{format}"})

# COLOR PICKER
COLOR_PICKER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Color Picker</title>
</head>
<body>
    <h1>Upload an Image & Click to Pick a Color</h1>
    <form id="uploadForm">
        <input type="file" id="imageUpload" required>
        <button type="submit">Upload</button>
    </form>
    <br>
    <img id="uploadedImage" style="max-width: 500px; display: none; cursor: crosshair;">
    <p id="colorResult"></p>

    <script>
        document.getElementById("uploadForm").onsubmit = async function(event) {
            event.preventDefault();
            let fileInput = document.getElementById("imageUpload").files[0];
            let formData = new FormData();
            formData.append("image", fileInput);
            
            let response = await fetch("/upload-image", { method: "POST", body: formData });
            let data = await response.json();

            if (data.url) {
                let imgElement = document.getElementById("uploadedImage");
                imgElement.src = data.url;
                imgElement.style.display = "block";
            }
        };

        document.getElementById("uploadedImage").onclick = async function(event) {
            let imgElement = event.target;
            let rect = imgElement.getBoundingClientRect();
            let x = event.clientX - rect.left;
            let y = event.clientY - rect.top;

            let response = await fetch(`/get-color?x=${x}&y=${y}`);
            let data = await response.json();

            document.getElementById("colorResult").innerHTML = `Color: RGB(${data.rgb}) - HEX: ${data.hex}`;
        };
    </script>
</body>
</html>
"""

@app.get("/colorpicker", response_class=HTMLResponse)
async def color_picker_page():
    return COLOR_PICKER_HTML

image_path = "/tmp/uploaded_image.png"

@app.post("/upload-image")
async def upload_image(image: UploadFile):
    with open(image_path, "wb") as f:
        f.write(await image.read())
    return JSONResponse({"url": "/display-image"})

@app.get("/get-color")
async def get_color(x: int, y: int):
    img = Image.open(image_path)
    rgb = img.convert("RGB").getpixel((x, y))
    hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)
    return JSONResponse({"rgb": rgb, "hex": hex_color})

# AUDIO CONVERTER
@app.post("/audioconverter")
async def convert_audio(audio: UploadFile, format: str = Form("mp3")):
    input_path = f"/tmp/{audio.filename}"
    output_path = f"/tmp/converted.{format}"
    with open(input_path, "wb") as f:
        f.write(await audio.read())

    ffmpeg.input(input_path).output(output_path).run()

    return JSONResponse({"url": f"/download?file=converted.{format}"})

# VIDEO CONVERTER
@app.post("/videoconverter")
async def convert_video(video: UploadFile, format: str = Form("mp4")):
    input_path = f"/tmp/{video.filename}"
    output_path = f"/tmp/converted.{format}"
    with open(input_path, "wb") as f:
        f.write(await video.read())

    ffmpeg.input(input_path).output(output_path).run()

    return JSONResponse({"url": f"/download?file=converted.{format}"})

@app.get("/download")
async def download_file(file: str):
    file_path = f"/tmp/{file}"
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=file)
    return JSONResponse({"error": "File not found"}, status_code=404)
