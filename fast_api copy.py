from fastapi import FastAPI, WebSocket
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
import time
from pydantic import BaseModel
from typing import Union

app = FastAPI()
templates = Jinja2Templates(directory="templates")

connected_clients = set()


class Item(BaseModel):
    data: float  # 必要に応じてJSONデータの構造を定義


@app.get("/test")
def read_root():
    return {"Hello": "World"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/stream")
async def stream(item: Item):
    print("test")
    print(f"Received JSON data: {item}")
    return {"message": "Data received successfully"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        previous_receive_time = None

        while True:
            data = await websocket.receive_text()
            print(data, flush=True)

            # 現在のタイムスタンプを取得
            current_receive_time = time.time()

            # 前回受信時刻があれば、経過時間を計算して表示
            if previous_receive_time is not None:
                elapsed_time_ms = (current_receive_time -
                                   previous_receive_time) * 1000
                print(
                    f"Elapsed time since last message: {elapsed_time_ms:.0f} ms")

            # クライアントからのデータを処理するコード
            await websocket.send_text(f"Message text was: {data}")

            # 現在のタイムスタンプを前回受信時刻として保存
            previous_receive_time = current_receive_time
    except WebSocketDisconnect as e:
        print(f"WebSocket connection closed with code {e.code}")
    finally:
        connected_clients.remove(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000,
                ssl_keyfile="/key.pem", ssl_certfile="/cert.pem")
