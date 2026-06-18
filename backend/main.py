from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/", StaticFiles(directory="static", html=True))

active_users = {}


async def broadcast(message):
    for ws in active_users.values():
        await ws.send_json(message)


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):

    await websocket.accept()

    # 用户名重复
    if username in active_users:
        await websocket.send_json({
            "type": "error",
            "msg": "用户名已存在"
        })
        await websocket.close()
        return

    active_users[username] = websocket

    # 通知上线
    await broadcast({
        "type": "system",
        "msg": f"{username}进入聊天室"
    })

    # 更新在线列表
    await broadcast({
        "type": "users",
        "users": list(active_users.keys())
    })

    try:
        while True:
            data = await websocket.receive_json()

            await broadcast({
                "type": "chat",
                "user": username,
                "msg": data["msg"]
            })

    except WebSocketDisconnect:

        del active_users[username]

        await broadcast({
            "type": "system",
            "msg": f"{username}离开聊天室"
        })

        await broadcast({
            "type": "users",
            "users": list(active_users.keys())
        })