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
  ├──▶ PostgreSQL 16 (serviço "db" no docker compose, volume pgdata)
  └──▶ Integração externa: ViaCEP (enriquecimento de endereço)
```

> **Nota:** existe também um protótipo anterior publicado na AWS
> (S3 + API Gateway + Lambda + DynamoDB), mantido apenas como prova de conceito.
> A fonte da verdade do projeto é este repositório (FastAPI + Docker).

---

## ✅ Funcionalidades

- 📋 Formulário de denúncia com campos obrigatórios e opcionais
- 🔒 100% anônimo — sem coleta de dados pessoais
- 🔑 Geração automática de protocolo único
- 🌍 Enriquecimento de endereço via CEP (API pública ViaCEP)
- 🗄️ Denúncias gravadas em PostgreSQL (persistem entre reinícios e deploys)
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
│   ├── ROLLBACK.md         # Versionamento semântico e simulação de rollback
│   └── evidencias/         # Prints da simulação de rollback
├── templates/              # Templates Jinja2
├── .dockerignore
├── .flake8                 # Configuração do lint
├── main.py                 # Aplicação FastAPI
├── test_integracao.py      # Testes de integração e mockados (ViaCEP)
├── test_persistencia.py    # Testes de persistência (JSON e PostgreSQL)
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

Acesse `http://localhost:8000`. Sobem dois serviços: `app` (FastAPI) e `db`
(PostgreSQL 16). Os dados ficam no volume `pgdata`.

A senha do banco vem da variável `POSTGRES_PASSWORD` (crie um arquivo `.env` com
`POSTGRES_PASSWORD=sua_senha`, sem caracteres especiais). Sem ela, vale um valor
padrão apenas para desenvolvimento local.

Para rodar uma versão publicada específica (imagem do GHCR):

```bash
APP_TAG=1.0.0 docker compose pull app
APP_TAG=1.0.0 docker compose up -d --no-build
```

Imagem publicada: `ghcr.io/helenojr05/sistema-denuncias` (tags `X.Y.Z` e `latest`).

### Sem Docker

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Sem a variável `DATABASE_URL`, a aplicação grava em arquivo JSON local
(`denuncias.json`), útil só para desenvolvimento. Para usar um PostgreSQL próprio:

```bash
export DATABASE_URL=postgresql://usuario:senha@localhost:5432/denuncias
uvicorn main:app --reload      # a tabela é criada na inicialização
```

---

## 🧪 Testes

```bash
pip install -r requirements.txt

pytest                   # testes mockados (padrão, sem internet; é o que o CI roda)
pytest -m integration    # apenas os testes reais contra o ViaCEP (requer internet)

# teste de persistência contra um PostgreSQL real (o CI sobe um automaticamente)
TEST_DATABASE_URL=postgresql://denuncias:denuncias@localhost:5432/denuncias pytest -m postgres
```

---

## 🔄 CI/CD

**CI** (`ci.yml`): a cada push/PR para `main` roda `flake8` e `pytest`, com um
PostgreSQL descartável como serviço do job para os testes de persistência.
A `main` é protegida por um ruleset: push direto bloqueado (sem bypass),
merge somente via Pull Request e com o check `build` do CI verde.

**CD** (`cd.yml`): ao criar uma tag `vX.Y.Z`:

1. Testes
2. Build da imagem e push no **GitHub Container Registry** (`X.Y.Z` e `latest`)
3. Release no GitHub com notas automáticas
4. Deploy simulado no ambiente `homologacao`: pull da imagem, `docker compose`
   com app + PostgreSQL e smoke test (`/health`, grava uma denúncia, confere a
   linha no banco e confere que ela sobrevive ao reinício da aplicação)

**Segredos:** nenhuma credencial fica no código nem no repositório. O login no
registry usa o `GITHUB_TOKEN`, gerado automaticamente pelo GitHub Actions a cada
execução e descartado ao final. A senha do PostgreSQL no deploy simulado é
gerada aleatoriamente a cada execução (mascarada nos logs). O ambiente
`homologacao` não possui segredos cadastrados.

**Versionamento e rollback:** veja [docs/ROLLBACK.md](docs/ROLLBACK.md).

---

## ⚠️ Limitações conhecidas

- Sem migrações de esquema (a tabela é criada na inicialização, se não existir).
- O arquivo JSON continua como fallback para desenvolvimento local; produção usa PostgreSQL.
- `/admin/denuncias` ainda não tem autenticação; previsto para a A3.
- O ambiente de homologação é simulado (efêmero, roda no runner do GitHub Actions).

---

## 📞 Contatos de Emergência

- **190** — Polícia Militar
- **Disque 100** — Direitos Humanos (MMFDH)

---

## 🛠️ Tecnologias

Python 3.11 · FastAPI · Jinja2 · httpx · PostgreSQL 16 · psycopg · pytest · Docker · GitHub Actions · GHCR
