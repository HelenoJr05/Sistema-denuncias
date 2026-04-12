from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from typing import Optional
import json
import os
import uuid

app = FastAPI(title="Sistema de Denúncias Anônimas - Homofobia")

templates = Jinja2Templates(directory="templates")

DENUNCIAS_FILE = "denuncias.json"

def carregar_denuncias():
    if os.path.exists(DENUNCIAS_FILE):
        with open(DENUNCIAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_denuncia(denuncia: dict):
    denuncias = carregar_denuncias()
    denuncias.append(denuncia)
    with open(DENUNCIAS_FILE, "w", encoding="utf-8") as f:
        json.dump(denuncias, f, ensure_ascii=False, indent=2)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        return templates.TemplateResponse(request, "index.html")
    except TypeError:
        return templates.TemplateResponse("index.html", {"request": request})

@app.post("/denunciar", response_class=JSONResponse)
async def registrar_denuncia(
    data_ocorrido: str = Form(...),
    horario_ocorrido: Optional[str] = Form(None),
    local_ocorrido: str = Form(...),
    descricao_ocorrido: str = Form(...),
    descricao_individuo: str = Form(...),
    tipo_ocorrido: Optional[str] = Form(None),
):
    if horario_ocorrido:
        data_hora = f"{data_ocorrido} às {horario_ocorrido}"
    else:
        data_hora = f"{data_ocorrido} (horário não informado)"

    denuncia = {
        "id": str(uuid.uuid4())[:8].upper(),
        "protocolo": f"DEN-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}",
        "data_registro": datetime.now().isoformat(),
        "data_ocorrido": data_ocorrido,
        "horario_ocorrido": horario_ocorrido or "Não informado",
        "data_hora_formatada": data_hora,
        "local_ocorrido": local_ocorrido,
        "descricao_ocorrido": descricao_ocorrido,
        "descricao_individuo": descricao_individuo,
        "tipo_ocorrido": tipo_ocorrido or "Não especificado",
        "status": "Recebida"
    }
    salvar_denuncia(denuncia)
    return {
        "sucesso": True,
        "protocolo": denuncia["protocolo"],
        "mensagem": "Sua denúncia foi registrada com sucesso e será analisada em sigilo absoluto."
    }

@app.get("/admin/denuncias", response_class=HTMLResponse)
async def listar_denuncias(request: Request):
    denuncias = carregar_denuncias()
    context = {"denuncias": denuncias, "total": len(denuncias)}
    try:
        return templates.TemplateResponse(request, "admin.html", context)
    except TypeError:
        return templates.TemplateResponse("admin.html", {"request": request, **context})