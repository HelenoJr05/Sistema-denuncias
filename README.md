# 🛡️ Sistema de Denúncias Anônimas — Combate à Homofobia

Sistema web para registro anônimo de ocorrências de homofobia.

---

## ☁️ Arquitetura atual

```
Usuário
  │
  ▼
FastAPI (main.py) — /, /denunciar, /admin/denuncias, /api/cep/{cep}, /health
  │        └── templates Jinja2 (frontend servido pela própria API)
  ▼
Persistência em JSON (volume Docker /data/denuncias.json)
  │
  ▼
Integração externa: ViaCEP (enriquecimento de endereço)
```

> **Nota:** existe também um protótipo anterior publicado na AWS
> (S3 + API Gateway + Lambda), mantido apenas como prova de conceito.
> A fonte da verdade do projeto é este repositório (FastAPI + Docker).

---

## ✅ Funcionalidades

- 📋 Formulário de denúncia com campos obrigatórios e opcionais
- 🔒 100% anônimo — sem coleta de dados pessoais
- 🔑 Geração automática de protocolo único
- 🌍 Enriquecimento de endereço via CEP (API pública ViaCEP)
- 📊 Painel administrativo (`/admin/denuncias`)
- ❤️ Endpoint de saúde (`/health`) com a versão em execução

---

## 📁 Estrutura do Repositório

```
├── .github/workflows/
│   ├── ci.yml              # CI: lint + testes (push/PR)
│   ├── cd.yml              # CD: build, GHCR, release, deploy simulado (tag vX.Y.Z)
│   └── rollback.yml        # Rollback manual para uma versão anterior
├── docs/
│   └── ROLLBACK.md         # Versionamento semântico e simulação de rollback
├── templates/              # Templates Jinja2
├── main.py                 # Aplicação FastAPI
├── test_integracao.py      # Testes de integração e mockados
├── test_health.py          # Teste do /health
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
└── requirements.txt
```

---

## 🔌 Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Formulário de denúncia (HTML) |
| POST | `/denunciar` | Registra denúncia (form-data) |
| GET | `/api/cep/{cep}` | Consulta endereço no ViaCEP |
| GET | `/admin/denuncias` | Lista denúncias (HTML) |
| GET | `/health` | `{"status": "ok", "version": "X.Y.Z"}` |

Campos de `POST /denunciar`: `data_ocorrido`*, `local_ocorrido`*,
`descricao_ocorrido`*, `descricao_individuo`*, `horario_ocorrido`,
`tipo_ocorrido`, `cep_ocorrido` (*obrigatórios).

---

## 🚀 Rodando localmente

### Com Docker (recomendado)

```bash
git clone https://github.com/HelenoJr05/Sistema-denuncias
cd Sistema-denuncias
docker compose up --build
```

Acesse `http://localhost:8000`. Os dados ficam no volume `denuncias_data`.

Para rodar uma versão publicada específica (imagem do GHCR):

```bash
APP_TAG=1.0.0 docker compose pull app
APP_TAG=1.0.0 docker compose up -d --no-build
```

### Sem Docker

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 🧪 Testes

```bash
pip install -r requirements.txt

pytest                   # testes mockados (padrão, sem internet; é o que o CI roda)
pytest -m integration    # apenas os testes reais contra o ViaCEP (requer internet)
```

---

## 🔄 CI/CD

**CI** (`ci.yml`): a cada push/PR para `main` roda `flake8` e `pytest`.
A `main` é protegida: merge só via Pull Request com o CI verde.

**CD** (`cd.yml`): ao criar uma tag `vX.Y.Z`:

1. Testes
2. Build da imagem e push no **GitHub Container Registry** (`X.Y.Z` e `latest`)
3. Release no GitHub com notas automáticas
4. Deploy simulado no ambiente `homologacao` (pull da imagem + smoke test)

**Segredos:** nenhuma credencial fica no código. O login no registry usa o
`GITHUB_TOKEN` do Secrets Management do GitHub Actions.

**Versionamento e rollback:** veja [docs/ROLLBACK.md](docs/ROLLBACK.md).

---

## 📞 Contatos de Emergência

- **190** — Polícia Militar
- **Disque 100** — Direitos Humanos (MMFDH)

---

## 🛠️ Tecnologias

Python 3.11 · FastAPI · Jinja2 · httpx · pytest · Docker · GitHub Actions · GHCR
