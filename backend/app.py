"""FastAPI WebSocket Chat Room Application"""

import os
import json
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from websocket_manager import ConnectionManager
from user_manager import UserManager
from message_handler import MessageHandler

# Global managers
connection_manager = ConnectionManager()
user_manager = UserManager()
message_handler = MessageHandler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    print("WebSocket Chat Room Server Started")
    yield
    await connection_manager.close_all_connections()
    print("WebSocket Chat Room Server Stopped")


app = FastAPI(
    title="WebSocket Chat Room",
    description="Real-time chat room using FastAPI and WebSocket",
    version="1.0.0",
    lifespan=lifespan
)

# =========================
# Static Files Configuration
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "static")
)

print("Static directory:", STATIC_DIR)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

@app.get("/")
async def root():
    """Serve index page"""
    return FileResponse(
        os.path.join(STATIC_DIR, "index.html")
    )


@app.get("/chat")
async def chat():
    """Serve chat page"""
    return FileResponse(
        os.path.join(STATIC_DIR, "chat.html")
    )

@app.get("/api/users")
async def get_online_users():
    """Get list of all online users"""
    users = user_manager.get_all_users()
    return {
        "count": len(users),
        "users": users,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/messages")
async def get_messages(limit: int = 50):
    """Get historical messages"""
    messages = message_handler.get_recent_messages(limit)
    return {
        "count": len(messages),
        "messages": messages
    }


@app.post("/api/messages")
async def post_message(username: str, content: str):
    """Post a message"""

    if not username or not content:
        raise HTTPException(
            status_code=400,
            detail="Username and content are required"
        )

    message = message_handler.create_message(
        username=username,
        content=content,
        msg_type="message"
    )

    return message


@app.delete("/api/sessions/{username}")
async def delete_session(username: str):
    """Delete a user session"""

    if user_manager.get_user(username):
        await connection_manager.disconnect(username)
        user_manager.remove_user(username)

        return {
            "status": "success",
            "message": f"Session for {username} deleted"
        }

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )


@app.websocket("/ws/{username}")
async def websocket_endpoint(
    websocket: WebSocket,
    username: str
):
    """WebSocket endpoint for real-time chat"""

    # Validate username
    if not username or len(username) < 2:
        await websocket.close(
            code=1008,
            reason="Invalid username"
        )
        return

    # Check duplicate username
    if user_manager.get_user(username):
        await websocket.close(
            code=1008,
            reason="Username already in use"
        )
        return

    # Accept connection
    await connection_manager.connect(
        websocket,
        username
    )

    user_manager.add_user(username)

    try:

        # User login broadcast
        login_message = message_handler.create_message(
            username=username,
            content=f"{username} joined the chat",
            msg_type="login"
        )

        await connection_manager.broadcast(login_message)

        # Send user list
        users_list_message = {
            "type": "user_list",
            "users": user_manager.get_all_users(),
            "timestamp": datetime.now().isoformat()
        }

        await connection_manager.send_personal(
            username,
            users_list_message
        )

        # Send recent messages
        recent_messages = message_handler.get_recent_messages(20)

        for msg in recent_messages:
            await connection_manager.send_personal(
                username,
                msg
            )

        # Main loop
        while True:

            data = await websocket.receive_text()

            message_data = json.loads(data)

            # Public message
            if message_data.get("type") == "message":

                message = message_handler.create_message(
                    username=username,
                    content=message_data.get(
                        "content",
                        ""
                    ),
                    msg_type="message"
                )

                await connection_manager.broadcast(
                    message
                )

            # Private message
            elif message_data.get("type") == "private_message":

                target_user = message_data.get(
                    "target_user"
                )

                if (
                    target_user and
                    user_manager.get_user(target_user)
                ):

                    private_msg = (
                        message_handler.create_message(
                            username=username,
                            content=message_data.get(
                                "content",
                                ""
                            ),
                            msg_type="private_message",
                            target_user=target_user
                        )
                    )

                    await connection_manager.send_personal(
                        target_user,
                        private_msg
                    )

                    await connection_manager.send_personal(
                        username,
                        private_msg
                    )

            # Typing notification
            elif message_data.get("type") == "typing":

                typing_msg = {
                    "type": "typing",
                    "username": username,
                    "timestamp": datetime.now().isoformat()
                }

                await connection_manager.broadcast(
                    typing_msg,
                    exclude=username
                )

            # Heartbeat
            elif message_data.get("type") == "ping":

                pong_msg = {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }

                await connection_manager.send_personal(
                    username,
                    pong_msg
                )

    except WebSocketDisconnect:

        await connection_manager.disconnect(
            username
        )

        user_manager.remove_user(
            username
        )

        logout_message = (
            message_handler.create_message(
                username=username,
                content=f"{username} left the chat",
                msg_type="logout"
            )
        )

        await connection_manager.broadcast(
            logout_message
        )

        users_list_message = {
            "type": "user_list",
            "users": user_manager.get_all_users(),
            "timestamp": datetime.now().isoformat()
        }

        await connection_manager.broadcast(
            users_list_message
        )

    except Exception as e:

        print(
            f"Error in WebSocket connection for "
            f"{username}: {str(e)}"
        )

        await connection_manager.disconnect(
            username
        )

        user_manager.remove_user(
            username
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        log_level="info"
    )
