from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect
from typing import List
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, dict[str, WebSocket]] = {
            "esp32": {},
            "web": {}
        }

    async def connect(self, client_type: str, client_id: str, websocket: WebSocket):
        await websocket.accept()
        if client_type not in self.active_connections:
            self.active_connections[client_type] = {}
            
        self.active_connections[client_type][client_id] = websocket
        print(f"[{client_type.upper()}] Cliente {client_id} conectado.")

    def disconnect(self, client_type: str, client_id: str):
        if client_id in self.active_connections.get(client_type, {}):
            del self.active_connections[client_type][client_id]
            print(f"[{client_type.upper()}] Cliente {client_id} desconectado.")

    async def send_to_esp32(self, esp32_id: str, message: str):
        esp32_conn = self.active_connections["esp32"].get(esp32_id)
        if esp32_conn:
            await esp32_conn.send_text(message)
            return True
        return False


manager = ConnectionManager()

@app.websocket("/ws/esp32/{esp32_id}")
async def esp32_websocket_endpoint(websocket: WebSocket, esp32_id: str):
    await manager.connect("esp32", esp32_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"ESP32 [{esp32_id}] reporta: {data}")
            
            # for web_client in manager.active_connections.get("web", {}).values():
            #     await web_client.send_text(f"Update: {data}")

    except WebSocketDisconnect:
        manager.disconnect("esp32", esp32_id)



@app.websocket("/ws/web_client/{client_id}")
async def web_client_websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect("web", client_id, websocket)
    try:
        while True:
            
            command_message = await websocket.receive_text()
            data = json.loads(command_message)
            
            
            target_id = data.get("esp32_id")
            print(target_id)
            print(command_message)
            if  target_id == None:
                await websocket.send_text("ERROR: JSON inválido. Se requiere 'esp32_id' y 'command'.")
                print("Error: No es Json")
                continue

            sent = await manager.send_to_esp32(target_id, command_message)
            print("enviando")
            if sent:
                await websocket.send_text(f"Comando '{command_message}' enviado a {target_id}.")
            else:
                await websocket.send_text(f"ERROR: ESP32 {command_message} no está conectada.")

    except WebSocketDisconnect:
        manager.disconnect("web", client_id)