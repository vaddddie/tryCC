import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
import model

app = FastAPI()
templates = Jinja2Templates(directory="templates")
net = model.load_model()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            img_data = data_json['image']  # base64
            r_channel = data_json.get('r', 0)
            b_channel = data_json.get('g', 0)
            g_channel = data_json.get('b', 0)
            
            header, encoded = img_data.split(',', 1)
            img_bytes = base64.b64decode(encoded)

            # Конвертируем в numpy array
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
            img_np = np.array(img)  # формат HWC

            mask = model.get_face_mask(net, img_np)
            recolored = model.recolor_hair(img_np, mask, (r_channel, b_channel, g_channel))

            processed_img_np = recolored

            # Конвертируем обратно в JPEG base64
            pil_img = Image.fromarray(processed_img_np)
            buf = BytesIO()
            pil_img.save(buf, format='JPEG')
            processed_bytes = buf.getvalue()
            processed_base64 = "data:image/jpeg;base64," + base64.b64encode(processed_bytes).decode()

            await websocket.send_text(processed_base64)
    except WebSocketDisconnect:
        print("Client disconnected")