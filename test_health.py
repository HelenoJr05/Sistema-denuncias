from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_retorna_ok_e_versao():
    resp = client.get("/health")
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["status"] == "ok"
    assert "version" in corpo
