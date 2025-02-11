import os
import subprocess
from flask import Flask, request, send_file, render_template_string
from PIL import Image
from colorthief import ColorThief

app = Flask(__name__)

TEMPLATE_HOME = """
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

TEMPLATE_IMAGE_CONVERTER = """
<!DOCTYPE html>
<html>
<head>
    <title>Image Converter</title>
</head>
<body>
    <h1>Convert Image to Another Format</h1>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image" required>
        <select name="format">
            <option value="png">PNG</option>
            <option value="jpg">JPG</option>
            <option value="bmp">BMP</option>
            <option value="gif">GIF</option>
        </select>
        <button type="submit">Convert</button>
    </form>
</body>
</html>
"""

TEMPLATE_COLOR_PICKER = """
<!DOCTYPE html>
<html>
<head>
    <title>Color Picker</title>
</head>
<body>
    <h1>Upload an Image to Get Colors</h1>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image" required>
        <button type="submit">Get Colors</button>
    </form>
</body>
</html>
"""

TEMPLATE_AUDIO_CONVERTER = """
<!DOCTYPE html>
<html>
<head>
    <title>Audio Converter</title>
</head>
<body>
    <h1>Convert Audio to Another Format</h1>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="audio" required>
        <select name="format">
            <option value="mp3">MP3</option>
            <option value="wav">WAV</option>
            <option value="ogg">OGG</option>
        </select>
        <button type="submit">Convert</button>
    </form>
</body>
</html>
"""

TEMPLATE_VIDEO_CONVERTER = """
<!DOCTYPE html>
<html>
<head>
    <title>Video Converter</title>
</head>
<body>
    <h1>Convert Video to Another Format</h1>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="video" required>
        <select name="format">
            <option value="mp4">MP4</option>
            <option value="avi">AVI</option>
            <option value="mov">MOV</option>
        </select>
        <button type="submit">Convert</button>
    </form>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(TEMPLATE_HOME)

@app.route('/imageconverter', methods=['GET', 'POST'])
def image_converter():
    if request.method == 'POST':
        file = request.files['image']
        file_format = request.form['format']
        if file:
            filename = convert_image(file, file_format)
            return send_file(filename, as_attachment=True)
    return render_template_string(TEMPLATE_IMAGE_CONVERTER)

def convert_image(file, file_format):
    input_path = f"/tmp/{file.filename}"
    output_path = f"/tmp/{os.path.splitext(file.filename)[0]}.{file_format}"
    file.save(input_path)
    image = Image.open(input_path)
    image.save(output_path, file_format.upper())
    return output_path

@app.route('/color-picker', methods=['GET', 'POST'])
def color_picker():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = f"/tmp/{file.filename}"
            file.save(filename)
            color_thief = ColorThief(filename)
            dominant_color = color_thief.get_color(quality=1)
            return f"Dominant Color: RGB{dominant_color}"
    return render_template_string(TEMPLATE_COLOR_PICKER)

@app.route('/audioconverter', methods=['GET', 'POST'])
def audio_converter():
    if request.method == 'POST':
        file = request.files['audio']
        file_format = request.form['format']
        if file:
            filename = convert_audio(file, file_format)
            return send_file(filename, as_attachment=True)
    return render_template_string(TEMPLATE_AUDIO_CONVERTER)

def convert_audio(file, file_format):
    input_path = f"/tmp/{file.filename}"
    output_path = f"/tmp/{os.path.splitext(file.filename)[0]}.{file_format}"
    file.save(input_path)
    subprocess.run(["ffmpeg", "-i", input_path, output_path, "-y"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

@app.route('/videoconverter', methods=['GET', 'POST'])
def video_converter():
    if request.method == 'POST':
        file = request.files['video']
        file_format = request.form['format']
        if file:
            filename = convert_video(file, file_format)
            return send_file(filename, as_attachment=True)
    return render_template_string(TEMPLATE_VIDEO_CONVERTER)

def convert_video(file, file_format):
    input_path = f"/tmp/{file.filename}"
    output_path = f"/tmp/{os.path.splitext(file.filename)[0]}.{file_format}"
    file.save(input_path)
    subprocess.run(["ffmpeg", "-i", input_path, output_path, "-y"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
