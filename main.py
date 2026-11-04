from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional
import json
import os
import time
import uuid

import httpx
import psycopg
from fastapi import FastAPI, Request, Form
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

APP_VERSION = os.getenv("APP_VERSION", "dev")

# Persistência:
#   - com DATABASE_URL definida  -> PostgreSQL (modo usado no docker compose)
#   - sem DATABASE_URL           -> arquivo JSON (desenvolvimento local e testes)
DENUNCIAS_FILE = os.getenv("DENUNCIAS_FILE", "denuncias.json")


def database_url() -> Optional[str]:
    return os.getenv("DATABASE_URL") or None


# ─────────────────────────────────────────────
# Persistência: PostgreSQL
# ─────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS denuncias (
    id                   TEXT PRIMARY KEY,
    protocolo            TEXT NOT NULL UNIQUE,
    data_registro        TIMESTAMPTZ NOT NULL DEFAULT now(),
    data_ocorrido        TEXT NOT NULL,
    horario_ocorrido     TEXT NOT NULL,
    data_hora_formatada  TEXT NOT NULL,
    local_ocorrido       TEXT NOT NULL,
    cep_ocorrido         TEXT NOT NULL,
    endereco_enriquecido JSONB NOT NULL DEFAULT '{}'::jsonb,
    descricao_ocorrido   TEXT NOT NULL,
    descricao_individuo  TEXT NOT NULL,
    tipo_ocorrido        TEXT NOT NULL,
    status               TEXT NOT NULL DEFAULT 'Recebida'
)
"""

INSERT_SQL = """
INSERT INTO denuncias (
    id, protocolo, data_registro, data_ocorrido, horario_ocorrido,
    data_hora_formatada, local_ocorrido, cep_ocorrido, endereco_enriquecido,
    descricao_ocorrido, descricao_individuo, tipo_ocorrido, status
) VALUES (
    %(id)s, %(protocolo)s, %(data_registro)s, %(data_ocorrido)s, %(horario_ocorrido)s,
    %(data_hora_formatada)s, %(local_ocorrido)s, %(cep_ocorrido)s, %(endereco_enriquecido)s,
    %(descricao_ocorrido)s, %(descricao_individuo)s, %(tipo_ocorrido)s, %(status)s
)
"""


def init_db(tentativas: int = 30, espera: float = 1.0) -> None:
    """Cria a tabela se não existir. Aguarda o banco aceitar conexões."""
    ultimo_erro = None
    for _ in range(tentativas):
        try:
            with psycopg.connect(database_url()) as conn:
                conn.execute(SCHEMA_SQL)
            return
        except psycopg.OperationalError as erro:
            ultimo_erro = erro
            time.sleep(espera)
    raise RuntimeError(f"Banco de dados indisponível: {ultimo_erro}")


def _salvar_postgres(denuncia: dict) -> None:
    registro = dict(denuncia)
    registro["endereco_enriquecido"] = Jsonb(denuncia["endereco_enriquecido"])
    with psycopg.connect(database_url()) as conn:
        conn.execute(INSERT_SQL, registro)


def _carregar_postgres() -> list:
    with psycopg.connect(database_url(), row_factory=dict_row) as conn:
        linhas = conn.execute("SELECT * FROM denuncias ORDER BY data_registro").fetchall()
    for linha in linhas:
        linha["data_registro"] = linha["data_registro"].isoformat()
    return linhas


# ─────────────────────────────────────────────
# Persistência: arquivo JSON (fallback)
# ─────────────────────────────────────────────

def _carregar_json() -> list:
    if os.path.exists(DENUNCIAS_FILE):
        with open(DENUNCIAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _salvar_json(denuncia: dict) -> None:
    denuncias = _carregar_json()
    denuncias.append(denuncia)
    with open(DENUNCIAS_FILE, "w", encoding="utf-8") as f:
        json.dump(denuncias, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
# Interface de persistência usada pelas rotas
# ─────────────────────────────────────────────

def carregar_denuncias() -> list:
    return _carregar_postgres() if database_url() else _carregar_json()


def salvar_denuncia(denuncia: dict) -> None:
    if database_url():
        _salvar_postgres(denuncia)
    else:
        _salvar_json(denuncia)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if database_url():
        await run_in_threadpool(init_db)
    yield


app = FastAPI(title="Sistema de Denúncias Anônimas - Homofobia", lifespan=lifespan)

templates = Jinja2Templates(directory="templates")


# ─────────────────────────────────────────────
# Integração com API pública: ViaCEP
# ─────────────────────────────────────────────

async def buscar_endereco_por_cep(cep: str) -> dict:
    """
    Consulta a API pública ViaCEP (https://viacep.com.br) para enriquecer
    o local da ocorrência com dados oficiais de endereço.
    Retorna um dicionário com os campos do endereço ou {} em caso de erro.
    """
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) != 8:
        return {}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if response.status_code == 200:
                dados = response.json()
                if "erro" not in dados:
                    return dados
    except (httpx.RequestError, httpx.TimeoutException):
        pass
    return {}


# ─────────────────────────────────────────────
# Rotas
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        return templates.TemplateResponse(request, "index.html")
    except TypeError:
        return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/cep/{cep}", response_class=JSONResponse)
async def consultar_cep(cep: str):
    """
    Endpoint que recebe um CEP e retorna os dados do endereço via ViaCEP.
    Usado pelo frontend para autocompletar o campo de local.
    """
    dados = await buscar_endereco_por_cep(cep)
    if not dados:
        return JSONResponse(
            content={"erro": "CEP não encontrado ou inválido."},
            status_code=404
        )
    return dados


@app.post("/denunciar", response_class=JSONResponse)
async def registrar_denuncia(
    data_ocorrido: str = Form(...),
    horario_ocorrido: Optional[str] = Form(None),
    local_ocorrido: str = Form(...),
    descricao_ocorrido: str = Form(...),
    descricao_individuo: str = Form(...),
    tipo_ocorrido: Optional[str] = Form(None),
    cep_ocorrido: Optional[str] = Form(None),
):
    if horario_ocorrido:
        data_hora = f"{data_ocorrido} às {horario_ocorrido}"
    else:
        data_hora = f"{data_ocorrido} (horário não informado)"

    # Enriquecimento com dados do ViaCEP (se CEP fornecido)
    dados_endereco = {}
    if cep_ocorrido:
        dados_endereco = await buscar_endereco_por_cep(cep_ocorrido)

    agora = datetime.now(timezone.utc)
    denuncia = {
        "id": str(uuid.uuid4())[:8].upper(),
        "protocolo": f"DEN-{agora.strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        "data_registro": agora.isoformat(),
        "data_ocorrido": data_ocorrido,
        "horario_ocorrido": horario_ocorrido or "Não informado",
        "data_hora_formatada": data_hora,
        "local_ocorrido": local_ocorrido,
        "cep_ocorrido": cep_ocorrido or "Não informado",
        "endereco_enriquecido": dados_endereco,  # dados vindos do ViaCEP
        "descricao_ocorrido": descricao_ocorrido,
        "descricao_individuo": descricao_individuo,
        "tipo_ocorrido": tipo_ocorrido or "Não especificado",
        "status": "Recebida"
    }

    await run_in_threadpool(salvar_denuncia, denuncia)

    return {
        "sucesso": True,
        "protocolo": denuncia["protocolo"],
        "endereco_confirmado": dados_endereco.get("logradouro", ""),
        "mensagem": "Sua denúncia foi registrada com sucesso e será analisada em sigilo absoluto."
    }


@app.get("/admin/denuncias", response_class=HTMLResponse)
async def listar_denuncias(request: Request):
    denuncias = await run_in_threadpool(carregar_denuncias)
    context = {"denuncias": denuncias, "total": len(denuncias)}
    try:
        return templates.TemplateResponse(request, "admin.html", context)
    except TypeError:
        return templates.TemplateResponse("admin.html", {"request": request, **context})


@app.get("/health", response_class=JSONResponse)
async def health():
    return {"status": "ok", "version": APP_VERSION}
