from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
import asyncio

import uvicorn

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connection: WebSocket = None
        self.loop = asyncio.get_event_loop()

    def connect(self, websocket: WebSocket):
        self.loop.run_until_complete(websocket.accept())
        self.active_connection = websocket

    def disconnect(self):
        self.active_connection = None

    def receive_message(self):
        if self.active_connection:
            try:
                return self.loop.run_until_complete(self.active_connection.receive_text())
            except WebSocketDisconnect:
                self.disconnect()
                raise HTTPException(status_code=400, detail="WebSocket disconnected")
        else:
            raise HTTPException(status_code=400, detail="No active WebSocket connection")

manager = ConnectionManager()

@app.websocket("/echo")
def websocket_endpoint(websocket: WebSocket):
    manager.connect(websocket)
    try:
        while True:
            # ここでは何もしないで接続を維持
            pass
    except WebSocketDisconnect:
        manager.disconnect()

@app.get("/wsx")
def wsxf():
    return manager.receive_message()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")