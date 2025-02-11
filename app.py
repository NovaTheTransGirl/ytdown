import os
import subprocess
from flask import Flask, request, send_file, render_template_string
from PIL import Image

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Image to PNG Converter</title>
</head>
<body>
    <h1>Image to PNG Converter</h1>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="image" required>
        <button type="submit">Convert</button>
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = convert_to_png(file)
            return send_file(filename, as_attachment=True)
    return render_template_string(TEMPLATE)

def convert_to_png(file):
    input_path = f"/tmp/{file.filename}"
    output_path = f"/tmp/{os.path.splitext(file.filename)[0]}.png"
    file.save(input_path)
    image = Image.open(input_path)
    image.save(output_path, "PNG")
    return output_path

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
