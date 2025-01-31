import os
import subprocess
from flask import Flask, request, send_file, render_template_string

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Downloader</title>
</head>
<body>
    <h1>YouTube Downloader</h1>
    <form method="POST">
        <input type="text" name="url" placeholder="Enter YouTube URL" required>
        <select name="format">
            <option value="mp4">MP4 (Best Quality)</option>
            <option value="mp3">MP3 (Audio Only)</option>
        </select>
        <button type="submit">Download</button>
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        format = request.form['format']
        filename = download_video(url, format)
        return send_file(filename, as_attachment=True)
    return render_template_string(TEMPLATE)

def download_video(url, format):
    output_path = "/tmp/%(title)s.%(ext)s"
    command = [
        "./yt-dlp", "-f", "bestaudio/best" if format == "mp3" else "bestvideo+bestaudio/best",
        "--output", output_path
    ]
    
    if format == "mp3":
        command.extend([
            "--postprocessor-args", f"-vn -b:a 320k -ffmpeg-location ./ffmpeg"
        ])
    
    subprocess.run(command, check=True)
    
    return output_path.replace("%(title)s", "video").replace("%(ext)s", format)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
