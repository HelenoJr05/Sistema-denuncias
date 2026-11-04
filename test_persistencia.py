"""
Testes de persistência: modo JSON (padrão) e PostgreSQL real.

O teste com PostgreSQL só roda quando TEST_DATABASE_URL está definida
(o CI sobe um serviço postgres e define essa variável):

    TEST_DATABASE_URL=postgresql://denuncias:denuncias@localhost:5432/denuncias pytest -m postgres
"""

import os
import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

import main
from main import app

DENUNCIA = {
    "data_ocorrido": "2026-01-10",
    "horario_ocorrido": "18:45",
    "local_ocorrido": "Praça central",
    "descricao_ocorrido": "Descrição de teste.",
    "descricao_individuo": "Pessoa não identificada.",
    "tipo_ocorrido": "Agressão verbal",
}


def test_denuncia_e_gravada_no_json_sem_database_url(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(main, "DENUNCIAS_FILE", str(tmp_path / "denuncias.json"))

    with TestClient(app) as client:
        resp = client.post("/denunciar", data=DENUNCIA)

    assert resp.status_code == 200
    salvas = main.carregar_denuncias()
    assert [d["protocolo"] for d in salvas] == [resp.json()["protocolo"]]
    assert salvas[0]["status"] == "Recebida"


@pytest.mark.postgres
@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL não definida")
def test_denuncia_persiste_no_postgres(tmp_path, monkeypatch):
    url = os.environ["TEST_DATABASE_URL"]
    monkeypatch.setenv("DATABASE_URL", url)
    arquivo_json = tmp_path / "denuncias.json"
    monkeypatch.setattr(main, "DENUNCIAS_FILE", str(arquivo_json))
    marcador = f"teste-postgres-{uuid.uuid4()}"

    # "with" executa o lifespan, que cria a tabela
    with TestClient(app) as client:
        resp = client.post("/denunciar", data={**DENUNCIA, "local_ocorrido": marcador})
        assert resp.status_code == 200
        protocolo = resp.json()["protocolo"]

    # Confere direto no banco (e não no arquivo JSON): a linha existe de verdade
    with psycopg.connect(url) as conn:
        linha = conn.execute(
            "SELECT local_ocorrido, status FROM denuncias WHERE protocolo = %s", (protocolo,)
        ).fetchone()
    assert linha == (marcador, "Recebida")
    assert not arquivo_json.exists()

    # A listagem usada pelo painel também lê do banco
    assert protocolo in [d["protocolo"] for d in main.carregar_denuncias()]

    with psycopg.connect(url) as conn:
        conn.execute("DELETE FROM denuncias WHERE local_ocorrido = %s", (marcador,))
