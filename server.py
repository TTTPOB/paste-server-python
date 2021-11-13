from typing import List
import time
import random
import string
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel


class device(BaseModel):
    userid: str
    pubkey: str


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/register")
async def register(device: device):
    return device


class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def send_personal(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for websocket in self.connections:
            await websocket.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{userid}/{pubkey_hash}")
async def ws_client(userid: str, pubkey_hash: str, websocket: WebSocket):
    await manager.connect(websocket)
    print(userid)
    try:
        while True:
            data = await websocket.receive_text()
            print(repr(data))
            await manager.send_personal(websocket, data)
            print(repr(data))
            # await manager.broadcast(f"haha, client{client_id} said{data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"client{userid} left")
