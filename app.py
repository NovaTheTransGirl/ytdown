import os
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from PIL import Image

app = FastAPI()

HTML_TEMPLATE = """
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

@app.get("/color-picker", response_class=HTMLResponse)
async def color_picker_page():
    return HTML_TEMPLATE

image_path = "/tmp/uploaded_image.png"

@app.post("/upload-image")
async def upload_image(image: UploadFile):
    with open(image_path, "wb") as f:
        f.write(await image.read())
    return JSONResponse({"url": "/display-image"})

@app.get("/display-image")
async def display_image():
    return HTMLResponse(f'<img src="/tmp/uploaded_image.png" style="max-width:500px;">')

@app.get("/get-color")
async def get_color(x: int, y: int):
    img = Image.open(image_path)
    rgb = img.convert("RGB").getpixel((x, y))
    hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)
    return JSONResponse({"rgb": rgb, "hex": hex_color})
