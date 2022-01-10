from fastapi import FastAPI, WebSocket, WebSocketDisconnect
app = FastAPI()

@app.websocket("/ws")
async def ws_connected(ws: WebSocket):
    await ws.accept()
    print("connected")
    try:
        while True:
            text = await ws.receive_text()
            await ws.send_text(text)
            print("received: " )
            print(repr(text))
            print("\n"*2)
    except WebSocketDisconnect:
        print("Client disconnected")