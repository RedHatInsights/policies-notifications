from starlette.testclient import TestClient

from app.main import notif_app


def test_get_apps():
    with TestClient(notif_app) as client:
        response = client.get("/apps")
        assert response.status_code == 200
