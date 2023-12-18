from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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
    print(f"{item}")
    return {"message": "Data received successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000,
                ssl_keyfile="/key.pem", ssl_certfile="/cert.pem")
