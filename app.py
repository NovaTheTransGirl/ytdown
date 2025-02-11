import os
import subprocess
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, HTMLResponse
from PIL import Image
from colorthief import ColorThief

app = FastAPI()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Media Converter</title>
</head>
<body>
    <h1>Welcome to Media Converter</h1>
    <ul>
        <li><a href="/imageconverter">Image Converter</a></li>
        <li><a href="/color-picker">Color Picker</a></li>
        <li><a href="/audioconverter">Audio Converter</a></li>
        <li><a href="/videoconverter">Video Converter</a></li>
    </ul>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

@app.get("/imageconverter", response_class=HTMLResponse)
async def image_converter_page():
    return """
    <h1>Convert Image to Another Format</h1>
    <form method="POST" enctype="multipart/form-data" action="/imageconverter">
        <input type="file" name="image" required>
        <select name="format">
            <option value="png">PNG</option>
            <option value="jpg">JPG</option>
            <option value="bmp">BMP</option>
            <option value="gif">GIF</option>
        </select>
        <button type="submit">Convert</button>
    </form>
    """

@app.post("/imageconverter")
async def convert_image(image: UploadFile, format: str = Form("png")):
    input_path = f"/tmp/{image.filename}"
    output_path = f"/tmp/{os.path.splitext(image.filename)[0]}.{format}"
    with open(input_path, "wb") as f:
        f.write(await image.read())
    img = Image.open(input_path)
    img.save(output_path, format.upper())
    return FileResponse(output_path, filename=os.path.basename(output_path))

@app.get("/color-picker", response_class=HTMLResponse)
async def color_picker_page():
    return """
    <h1>Upload an Image to Get Colors</h1>
    <form method="POST" enctype="multipart/form-data" action="/color-picker">
        <input type="file" name="image" required>
        <button type="submit">Get Colors</button>
    </form>
    """

@app.post("/color-picker")
async def color_picker(image: UploadFile):
    input_path = f"/tmp/{image.filename}"
    with open(input_path, "wb") as f:
        f.write(await image.read())
    color_thief = ColorThief(input_path)
    dominant_color = color_thief.get_color(quality=1)
    return {"Dominant Color (RGB)": dominant_color}

@app.get("/audioconverter", response_class=HTMLResponse)
async def audio_converter_page():
    return """
    <h1>Convert Audio to Another Format</h1>
    <form method="POST" enctype="multipart/form-data" action="/audioconverter">
        <input type="file" name="audio" required>
        <select name="format">
            <option value="mp3">MP3</option>
            <option value="wav">WAV</option>
            <option value="ogg">OGG</option>
        </select>
        <button type="submit">Convert</button>
    </form>
    """

@app.post("/audioconverter")
async def convert_audio(audio: UploadFile, format: str = Form("mp3")):
    input_path = f"/tmp/{audio.filename}"
    output_path = f"/tmp/{os.path.splitext(audio.filename)[0]}.{format}"
    with open(input_path, "wb") as f:
        f.write(await audio.read())
    subprocess.run(["ffmpeg", "-i", input_path, output_path, "-y"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return FileResponse(output_path, filename=os.path.basename(output_path))

@app.get("/videoconverter", response_class=HTMLResponse)
async def video_converter_page():
    return """
    <h1>Convert Video to Another Format</h1>
    <form method="POST" enctype="multipart/form-data" action="/videoconverter">
        <input type="file" name="video" required>
        <select name="format">
            <option value="mp4">MP4</option>
            <option value="avi">AVI</option>
            <option value="mov">MOV</option>
        </select>
        <button type="submit">Convert</button>
    </form>
    """

@app.post("/videoconverter")
async def convert_video(video: UploadFile, format: str = Form("mp4")):
    input_path = f"/tmp/{video.filename}"
    output_path = f"/tmp/{os.path.splitext(video.filename)[0]}.{format}"
    with open(input_path, "wb") as f:
        f.write(await video.read())
    subprocess.run(["ffmpeg", "-i", input_path, output_path, "-y"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return FileResponse(output_path, filename=os.path.basename(output_path))
