"""
Teste de Integração — Sistema de Denúncias Anônimas
=====================================================
Valida a comunicação da aplicação com a API pública ViaCEP.

Como executar:
    pip install pytest pytest-asyncio httpx
    pytest test_integracao.py -v
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

# Importa a app e a função de integração
from main import app, buscar_endereco_por_cep


# ─────────────────────────────────────────────────────────────
# 1. TESTE REAL — chama a API ViaCEP de verdade
#    (requer conexão com internet; use -m integration para rodar)
# ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.integration
async def test_viacep_cep_valido_retorna_dados():
    """
    Integração real: garante que a API ViaCEP responde corretamente
    para um CEP válido e que os campos essenciais estão presentes.
    """
    dados = await buscar_endereco_por_cep("01310100")  # Av. Paulista, SP
    assert dados != {}, "A API deve retornar dados para um CEP válido"
    assert "logradouro" in dados
    assert "localidade" in dados
    assert "uf" in dados
    assert dados["uf"] == "SP"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_viacep_cep_invalido_retorna_vazio():
    """
    Integração real: garante que um CEP inválido retorna dicionário vazio.
    """
    dados = await buscar_endereco_por_cep("00000000")
    assert dados == {}, "CEP inválido deve retornar dicionário vazio"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_viacep_cep_mal_formatado():
    """
    Integração real: CEP com menos de 8 dígitos deve retornar vazio
    sem fazer requisição.
    """
    dados = await buscar_endereco_por_cep("1234")
    assert dados == {}


# ─────────────────────────────────────────────────────────────
# 2. TESTES MOCKADOS — não dependem de internet (CI/CD friendly)
# ─────────────────────────────────────────────────────────────

MOCK_VIACEP_RESPONSE = {
    "cep": "70040-010",
    "logradouro": "Esplanada dos Ministérios",
    "complemento": "",
    "bairro": "Zona Cívico-Administrativa",
    "localidade": "Brasília",
    "uf": "DF",
    "ibge": "5300108",
    "gia": "",
    "ddd": "61",
    "siafi": "9701"
}


@pytest.mark.asyncio
async def test_endpoint_cep_valido_mock():
    """
    Testa o endpoint /api/cep/{cep} com resposta mockada do ViaCEP.
    Garante que o fluxo interno da aplicação processa corretamente os dados.
    """
    with patch("main.buscar_endereco_por_cep", new_callable=AsyncMock) as mock_cep:
        mock_cep.return_value = MOCK_VIACEP_RESPONSE

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/cep/70040010")

        assert response.status_code == 200
        dados = response.json()
        assert dados["localidade"] == "Brasília"
        assert dados["uf"] == "DF"
        assert dados["logradouro"] == "Esplanada dos Ministérios"


@pytest.mark.asyncio
async def test_endpoint_cep_invalido_retorna_404_mock():
    """
    Testa que o endpoint /api/cep/{cep} retorna 404 quando o CEP não existe.
    """
    with patch("main.buscar_endereco_por_cep", new_callable=AsyncMock) as mock_cep:
        mock_cep.return_value = {}  # simula CEP não encontrado

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/cep/00000000")

        assert response.status_code == 404
        assert "erro" in response.json()


@pytest.mark.asyncio
async def test_registrar_denuncia_com_cep_enriquece_dados_mock():
    """
    Testa o endpoint POST /denunciar com CEP informado.
    Verifica que a denúncia é registrada e o endereço é enriquecido com dados do ViaCEP.
    """
    with patch("main.buscar_endereco_por_cep", new_callable=AsyncMock) as mock_cep:
        mock_cep.return_value = MOCK_VIACEP_RESPONSE

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/denunciar", data={
                "data_ocorrido": "2025-06-01",
                "horario_ocorrido": "14:30",
                "local_ocorrido": "Esplanada dos Ministérios, Brasília",
                "descricao_ocorrido": "Xingamentos e agressões verbais.",
                "descricao_individuo": "Homem, aparentando 40 anos.",
                "tipo_ocorrido": "Agressão verbal",
                "cep_ocorrido": "70040010",
            })

        assert response.status_code == 200
        dados = response.json()
        assert dados["sucesso"] is True
        assert "protocolo" in dados
        assert dados["protocolo"].startswith("DEN-")
        assert dados["endereco_confirmado"] == "Esplanada dos Ministérios"


@pytest.mark.asyncio
async def test_registrar_denuncia_sem_cep_funciona_normalmente():
    """
    Testa que o endpoint POST /denunciar funciona mesmo sem CEP.
    O campo é opcional; a denúncia deve ser salva normalmente.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/denunciar", data={
            "data_ocorrido": "2025-06-01",
            "local_ocorrido": "Centro de Brasília",
            "descricao_ocorrido": "Discriminação em local público.",
            "descricao_individuo": "Não identificado.",
        })

    assert response.status_code == 200
    dados = response.json()
    assert dados["sucesso"] is True
    assert "protocolo" in dados
