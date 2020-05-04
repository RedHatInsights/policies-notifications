import os

os.system('uvicorn app.main:notif_app --host 0.0.0.0 --log-config=logging.ini')
