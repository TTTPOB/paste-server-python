from typing import List
import time
import jwt
import random
import string
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.get("register")
async def register(websocket: WebSocket):
    return


class ConnectionManager:
    def __init__(self):
	    self.connections:List[WebSocket] = []
    async def connect(self, websocket:WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
    def disconnect(self, websocket:WebSocket):
        self.connections.remove(websocket)
    async def send_personal(self, websocket:WebSocket, message:str):
        await websocket.send_text(message)
    async def broadcast(self, message:str):
        for websocket in self.connections:
            await websocket.send_text(message)
manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def ws_client(client_id:str, websocket:WebSocket):
    await manager.connect(websocket)
    print(client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal(websocket, data)
            print(repr(data))
            # await manager.broadcast(f"haha, client{client_id} said{data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"client{client_id} left")

