"""
WebSocket Chat Room - Main Entry Point
使用 app.py 中的完整实现
"""
from backend.app import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
