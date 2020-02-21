import uvicorn

from app.main import notif_app

if __name__ == "__main__":
    uvicorn.run(notif_app, host="0.0.0.0")
