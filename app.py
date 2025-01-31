import os
import yt_dlp
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
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if format == 'mp4' else 'bestaudio',
        'outtmpl': f'%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }] if format == 'mp3' else []
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
